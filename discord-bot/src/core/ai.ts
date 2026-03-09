import { AIService, MemoryRedis } from '../../../shared';
import { createLogger } from './logger';
import { Redis } from 'ioredis';

const logger = createLogger('AI');

let redisClient: Redis | MemoryRedis;

if (process.env.REDIS_URL) {
    redisClient = new Redis(process.env.REDIS_URL);
    redisClient.on('error', (err: any) => logger.error('AI Redis Error:', err));
} else {
    logger.warn('REDIS_URL not set for AI Service. Using in-memory fallback.');
    redisClient = new MemoryRedis();
}

export const aiService = new AIService({
    anthropicApiKey:  process.env.ANTHROPIC_API_KEY         || '',
    defaultModel:     process.env.ANTHROPIC_MODEL           || 'claude-sonnet-4-6',
    botName:          process.env.BOT_NAME                  || 'SupportBot',
    escalationUserId: process.env.HUMAN_MODERATOR_CHANNEL   || '',
}, redisClient, logger);
