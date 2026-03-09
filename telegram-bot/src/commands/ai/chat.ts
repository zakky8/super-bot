import { Bot } from 'grammy';
import { BotContext } from '../../types';
import { aiService } from '../../core/ai';

export default (bot: Bot<BotContext>) => {

  // ── /chat — main AI chat command ──────────────────────────────────────────
  bot.command('chat', async (ctx: BotContext) => {
    try {
      const message = (ctx.match as string)?.trim();
      const userId  = ctx.from?.id?.toString() || 'unknown';

      if (!message) {
        return ctx.reply(
          '💬 *AI Chat*\n\n' +
          '*Usage:*\n' +
          '`/chat <your message>` — ask the AI anything\n' +
          '`/chat clear` — reset conversation history\n\n' +
          '*Examples:*\n' +
          '`/chat How do I reset my password?`\n' +
          '`/chat What are the trading fees?`\n\n' +
          'Need a human? Use `/support`',
          { parse_mode: 'Markdown' },
        );
      }

      const lower = message.toLowerCase();

      if (lower === 'clear') {
        await aiService.clearConversationContext(userId, ctx.chat?.id.toString(), 'telegram');
        return ctx.reply('🗑️ Conversation history cleared. Starting fresh!');
      }

      await ctx.replyWithChatAction('typing');

      try {
        const context  = await aiService.getConversationContext(userId, ctx.chat?.id.toString(), 'telegram');
        const response = await aiService.chat(context, message);

        // Escalation — human moderator needed
        if (response.isEscalation) {
          await ctx.reply(
            '🔔 *Connecting you to a human moderator*\n\n' +
            'I could not find the answer in my knowledge base.\n' +
            'A support agent has been notified and will follow up shortly.\n\n' +
            '_You can also use_ `/support` _to send a direct message to the team._',
            { parse_mode: 'Markdown' },
          );

          // Notify human moderator if configured
          const modChatId = process.env.HUMAN_MODERATOR_CHAT_ID;
          if (modChatId) {
            try {
              await ctx.api.sendMessage(
                parseInt(modChatId, 10),
                `⚠️ <b>ESCALATION NEEDED</b>\n` +
                `User: <code>${userId}</code>\n` +
                `Chat: <code>${ctx.chat?.id}</code>\n` +
                `Message: ${message.slice(0, 400)}`,
                { parse_mode: 'HTML' },
              );
            } catch (notifyErr) {
              console.error('Failed to notify moderator:', notifyErr);
            }
          }
          return;
        }

        // Normal response — split if over Telegram's 4096-char limit
        const text = response.content;
        if (text.length > 4000) {
          const chunks = text.match(/.{1,4000}/gs) || [text];
          for (const chunk of chunks) await ctx.reply(chunk);
        } else {
          await ctx.reply(text);
        }

      } catch (aiError: any) {
        console.error('AI Service Error:', aiError);
        const msg = String(aiError.message || '');
        if (msg.includes('Rate limit')) {
          await ctx.reply('⏳ You are sending messages too fast. Please wait a moment and try again.');
        } else {
          await ctx.reply('🤖 AI is temporarily unavailable. Please try again shortly or use `/support`.');
        }
      }

    } catch (error) {
      console.error('chat command error:', error);
      await ctx.reply('❌ Failed to process your request.');
    }
  });

  // ── /ask — alias for /chat ─────────────────────────────────────────────────
  bot.command('ask', async (ctx: BotContext) => {
    const message = (ctx.match as string)?.trim();
    if (!message) {
      return ctx.reply('Usage: `/ask <question>`\nExample: `/ask How do I reset my password?`', { parse_mode: 'Markdown' });
    }

    // Delegate to the same AI logic
    try {
      await ctx.replyWithChatAction('typing');
      const userId   = ctx.from?.id?.toString() || 'unknown';
      const context  = await aiService.getConversationContext(userId, ctx.chat?.id.toString(), 'telegram');
      const response = await aiService.chat(context, message);

      if (response.isEscalation) {
        await ctx.reply('🔔 I couldn\'t find an answer. Use `/support` to reach a human moderator.', { parse_mode: 'Markdown' });
        return;
      }

      await ctx.reply(response.content);

    } catch (err) {
      console.error('ask command error:', err);
      await ctx.reply('❌ AI is currently unavailable. Please try `/support` for human assistance.');
    }
  });

  // ── /support — escalate to human ──────────────────────────────────────────
  bot.command('support', async (ctx: BotContext) => {
    const message = (ctx.match as string)?.trim();
    const userId  = ctx.from?.id?.toString() || 'unknown';

    if (!message) {
      return ctx.reply(
        '🙋 *Human Support*\n\n' +
        'Describe your issue and a moderator will assist you:\n' +
        '`/support <your issue here>`\n\n' +
        '_Example:_ `/support My withdrawal has been pending for 3 days.`',
        { parse_mode: 'Markdown' },
      );
    }

    await ctx.reply(
      '✅ *Support request sent!*\n\n' +
      'A human moderator has been notified and will get back to you shortly.\n' +
      '_Average response time: under 1 hour._',
      { parse_mode: 'Markdown' },
    );

    const modChatId = process.env.HUMAN_MODERATOR_CHAT_ID;
    if (modChatId) {
      try {
        await ctx.api.sendMessage(
          parseInt(modChatId, 10),
          `🆘 <b>SUPPORT REQUEST</b>\n` +
          `User: <code>${userId}</code>\n` +
          `Name: ${ctx.from?.first_name || 'Unknown'}\n` +
          `Chat: <code>${ctx.chat?.id}</code>\n` +
          `Issue: ${message.slice(0, 500)}`,
          { parse_mode: 'HTML' },
        );
      } catch (err) {
        console.error('Failed to forward support request:', err);
      }
    } else {
      console.warn('HUMAN_MODERATOR_CHAT_ID not set — support request not forwarded');
    }
  });

};
