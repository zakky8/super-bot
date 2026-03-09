import { Bot } from 'grammy';
import { BotContext } from '../../types';
import { aiService, reinitializeAIService } from '../../core/ai';

export default (bot: Bot<BotContext>) => {
  bot.command('aisetup', async (ctx: BotContext) => {
    try {
      // Security: only allow in private chat
      if (ctx.chat && ctx.chat.type !== 'private') {
        return ctx.reply('🔒 This command only works in private chat with the bot (for security).');
      }

      const rawArgs = (ctx.match as string)?.trim() || '';
      const args    = rawArgs.split(' ').filter((a) => a.length > 0);

      if (!args[0]) {
        return ctx.reply(
          '🤖 *Anthropic Claude AI Setup*\n\n' +
          '*Usage:*\n' +
          '`/aisetup key <your_anthropic_key>`\n' +
          '`/aisetup model <model_name>`\n' +
          '`/aisetup test`\n' +
          '`/aisetup status`\n' +
          '`/aisetup faq` — reload FAQ knowledge base\n\n' +
          '*Available Claude Models:*\n' +
          '• `claude-sonnet-4-6` — Balanced *(default)*\n' +
          '• `claude-opus-4-5` — Most powerful\n' +
          '• `claude-haiku-4-5` — Fastest & cheapest\n' +
          '• `claude-3-5-sonnet-20241022` — Stable release\n' +
          '• `claude-3-haiku-20240307` — Ultra-fast\n\n' +
          '🔑 Get your API key: https://console.anthropic.com/',
          { parse_mode: 'Markdown' },
        );
      }

      const command = args[0].toLowerCase();
      const value   = args.slice(1).join(' ');

      // ── key ────────────────────────────────────────────────────────────────
      if (command === 'key') {
        if (!value) {
          return ctx.reply('❌ Provide your Anthropic API key:\n`/aisetup key sk-ant-...`', { parse_mode: 'Markdown' });
        }
        // @ts-ignore — runtime env update for this session
        process.env.ANTHROPIC_API_KEY = value;
        reinitializeAIService();
        return ctx.reply(
          '✅ *Anthropic API key set for this session*\n\n' +
          '📋 *Next steps:*\n' +
          '1. Test: `/aisetup test`\n' +
          '2. Chat: `/chat Hello!`\n\n' +
          '📝 To make permanent, add to `.env`:\n' +
          `\`ANTHROPIC_API_KEY=${value.slice(0, 20)}...\``,
          { parse_mode: 'Markdown' },
        );
      }

      // ── model ──────────────────────────────────────────────────────────────
      if (command === 'model') {
        if (!value) {
          return ctx.reply(
            '❌ Provide a model name:\n`/aisetup model claude-sonnet-4-6`\n\n' +
            '*Available models:*\n' +
            '• `claude-sonnet-4-6` *(default)*\n• `claude-opus-4-5`\n• `claude-haiku-4-5`',
            { parse_mode: 'Markdown' },
          );
        }
        if (!process.env.ANTHROPIC_API_KEY) {
          return ctx.reply(
            '⚠️ Set your API key first:\n`/aisetup key sk-ant-...`',
            { parse_mode: 'Markdown' },
          );
        }
        // @ts-ignore
        process.env.ANTHROPIC_MODEL = value;
        reinitializeAIService();
        return ctx.reply(
          `✅ Model changed to \`${value}\`\n\n📝 To make permanent add to \`.env\`:\n\`ANTHROPIC_MODEL=${value}\``,
          { parse_mode: 'Markdown' },
        );
      }

      // ── status ─────────────────────────────────────────────────────────────
      if (command === 'status') {
        const hasKey = !!process.env.ANTHROPIC_API_KEY;
        const model  = process.env.ANTHROPIC_MODEL || 'claude-sonnet-4-6';
        const modId  = process.env.HUMAN_MODERATOR_CHAT_ID || 'not set';
        return ctx.reply(
          '🤖 *AI Configuration Status*\n\n' +
          `🔑 *Anthropic API:* ${hasKey ? '✅ Configured' : '❌ Not set'}\n` +
          `🧠 *Model:* \`${model}\`\n` +
          `📡 *Provider:* ${hasKey ? 'Anthropic Claude' : 'Ollama (fallback)'}\n` +
          `🙋 *Escalation chat:* \`${modId}\`\n` +
          `⚡ *Status:* ${hasKey ? '✅ Ready' : '⚠️ Set ANTHROPIC_API_KEY to enable Claude'}\n\n` +
          (hasKey ? 'Try `/chat hello` to start!' : 'Configure with `/aisetup key sk-ant-...`'),
          { parse_mode: 'Markdown' },
        );
      }

      // ── faq ────────────────────────────────────────────────────────────────
      if (command === 'faq') {
        aiService.reloadFaq();
        return ctx.reply('✅ FAQ knowledge base reloaded from faq_data.json');
      }

      // ── test ───────────────────────────────────────────────────────────────
      if (command === 'test') {
        if (!process.env.ANTHROPIC_API_KEY) {
          return ctx.reply('❌ Set API key first:\n`/aisetup key sk-ant-...`', { parse_mode: 'Markdown' });
        }
        await ctx.replyWithChatAction('typing');
        try {
          const context  = { userId: 'test', platform: 'telegram' as const, messages: [] };
          const response = await aiService.chat(context, 'Say "Claude is working!" in exactly 3 words.', { saveContext: false });
          const model    = process.env.ANTHROPIC_MODEL || 'claude-sonnet-4-6';
          return ctx.reply(
            `✅ *Anthropic Test Passed*\n\n🧠 Model: \`${model}\`\n💬 Response: ${response.content}\n🔢 Tokens: ${response.tokensUsed ?? 'n/a'}`,
            { parse_mode: 'Markdown' },
          );
        } catch (err) {
          return ctx.reply(
            `❌ *Anthropic Test Failed*\n\`${String(err).slice(0, 200)}\`\n\nCheck your API key with \`/aisetup status\``,
            { parse_mode: 'Markdown' },
          );
        }
      }

      return ctx.reply('❓ Unknown sub-command. Use `/aisetup` for help.');

    } catch (error) {
      console.error('aisetup error:', error);
      await ctx.reply('❌ An error occurred: ' + String(error).slice(0, 100));
    }
  });
};
