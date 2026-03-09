import {
  ChatInputCommandInteraction,
  SlashCommandBuilder,
  EmbedBuilder,
  Colors,
} from 'discord.js';
import { aiService } from '../../core/ai';

export default {
  data: new SlashCommandBuilder()
    .setName('chat')
    .setDescription('Chat with Claude AI — FAQ-aware support assistant')
    .addStringOption((o: any) =>
      o.setName('message')
        .setDescription('Your question or message')
        .setRequired(true),
    )
    .addBooleanOption((o: any) =>
      o.setName('clear')
        .setDescription('Clear your conversation history')
        .setRequired(false),
    ),

  category: 'ai',

  async execute(interaction: ChatInputCommandInteraction) {
    try {
      const message = interaction.options.getString('message', true);
      const clear   = interaction.options.getBoolean('clear');
      const userId  = interaction.user.id;

      // Clear history
      if (clear) {
        await aiService.clearConversationContext(userId, interaction.guildId ?? undefined, 'discord');
        return interaction.reply({ content: '🗑️ Conversation history cleared!', ephemeral: true });
      }

      await interaction.deferReply();

      try {
        const context  = await aiService.getConversationContext(userId, interaction.guildId ?? undefined, 'discord');
        const response = await aiService.chat(context, message);

        // Escalation — notify support channel if configured
        if (response.isEscalation) {
          const escalationChannelId = process.env.HUMAN_MODERATOR_CHANNEL;
          if (escalationChannelId) {
            try {
              const channel = await interaction.client.channels.fetch(escalationChannelId);
              if (channel?.isTextBased()) {
                await (channel as any).send(
                  `⚠️ **ESCALATION NEEDED**\n` +
                  `User: ${interaction.user.tag} (<@${userId}>)\n` +
                  `Guild: ${interaction.guild?.name ?? 'DM'}\n` +
                  `Question: ${message.slice(0, 500)}`,
                );
              }
            } catch (notifyErr) {
              console.error('Failed to notify escalation channel:', notifyErr);
            }
          }

          const escalationEmbed = new EmbedBuilder()
            .setColor(Colors.Orange)
            .setTitle('🔔 Connecting you to a human moderator')
            .setDescription(
              "I couldn't find an answer in my knowledge base.\n" +
              'A support agent has been notified and will follow up shortly.\n\n' +
              'You can also use `/support` to send a direct message to the team.',
            )
            .setFooter({ text: 'AI Support • Human escalation triggered' })
            .setTimestamp();

          return interaction.editReply({ embeds: [escalationEmbed] });
        }

        // Normal AI response
        const embed = new EmbedBuilder()
          .setColor(Colors.Blurple)
          .setAuthor({
            name:    interaction.user.tag,
            iconURL: interaction.user.displayAvatarURL(),
          })
          .setDescription(response.content.slice(0, 4096))
          .setFooter({
            text: `🤖 Claude AI • ${response.model} • /chat clear:true to reset`,
          })
          .setTimestamp();

        await interaction.editReply({ embeds: [embed] });

      } catch (aiError: any) {
        console.error('AI Service Error:', aiError);
        const msg = String(aiError.message || '');
        const text = msg.includes('Rate limit')
          ? '⏳ You are sending messages too fast. Please wait a moment and try again.'
          : '🤖 AI is temporarily unavailable. Use `/support` to reach a human moderator.';
        await interaction.editReply({ content: text });
      }

    } catch (error) {
      console.error('Error in /chat command:', error);
      const payload = { content: '❌ Failed to generate a response.' };
      if (interaction.replied || interaction.deferred) {
        await interaction.editReply(payload);
      } else {
        await interaction.reply({ ...payload, ephemeral: true });
      }
    }
  },
};
