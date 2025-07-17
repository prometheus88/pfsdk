/**
 * Unit tests for PostFiat gRPC service implementations
 */

import { describe, it, expect, beforeEach, jest } from '@jest/globals';
import { ContentStorageServiceImpl, EnvelopeStorageServiceImpl, AgentRegistryServiceImpl } from '../../../src/services';
import { StoreContentRequest, StoreEnvelopeRequest, StoreAgentCardRequest } from '../../../src/generated/postfiat/v3/messages_pb';
import { GetAgentCardRequest, AgentCard } from '../../../src/generated/a2a/v1/a2a_pb';
import { Envelope } from '../../../src/generated/postfiat/v3/messages_pb';

describe('PostFiat gRPC Service Implementations', () => {
  describe('ContentStorageServiceImpl', () => {
    let service: ContentStorageServiceImpl;

    beforeEach(() => {
      service = new ContentStorageServiceImpl();
    });

    it('should create service instance', () => {
      expect(service).toBeDefined();
      expect(service).toBeInstanceOf(ContentStorageServiceImpl);
    });

    it('should store content', async () => {
      const request = new StoreContentRequest();
      request.content = new TextEncoder().encode('test content');
      request.contentType = 'text/plain';

      const descriptor = await service.storeContent(request);
      
      expect(descriptor).toBeDefined();
      expect(descriptor.contentType).toBe('text/plain');
      expect(descriptor.contentLength).toBe(BigInt(12)); // 'test content'.length
    });

    it('should validate content requirements', async () => {
      const request = new StoreContentRequest();
      request.content = new Uint8Array();
      request.contentType = 'text/plain';

      await expect(service.storeContent(request)).rejects.toThrow('Content cannot be empty');
    });

    it('should validate content type requirements', async () => {
      const request = new StoreContentRequest();
      request.content = new TextEncoder().encode('test content');
      request.contentType = '';

      await expect(service.storeContent(request)).rejects.toThrow('Content type is required');
    });
  });

  describe('EnvelopeStorageServiceImpl', () => {
    let service: EnvelopeStorageServiceImpl;

    beforeEach(() => {
      service = new EnvelopeStorageServiceImpl();
    });

    it('should create service instance', () => {
      expect(service).toBeDefined();
      expect(service).toBeInstanceOf(EnvelopeStorageServiceImpl);
    });

    it('should validate envelope requirements', async () => {
      const request = new StoreEnvelopeRequest();
      // request.envelope is not set

      await expect(service.storeEnvelope(request)).rejects.toThrow('Envelope is required');
    });

    it('should validate envelope ID for retrieval', async () => {
      const request = { envelopeId: '' };

      await expect(service.retrieveEnvelope(request as any)).rejects.toThrow('Envelope ID is required');
    });
  });

  describe('AgentRegistryServiceImpl', () => {
    let service: AgentRegistryServiceImpl;

    beforeEach(() => {
      service = new AgentRegistryServiceImpl();
    });

    it('should create service instance', () => {
      expect(service).toBeDefined();
      expect(service).toBeInstanceOf(AgentRegistryServiceImpl);
    });

    it('should return default agent card', async () => {
      const request = new GetAgentCardRequest();

      const agentCard = await service.getAgentCard(request);
      
      expect(agentCard).toBeDefined();
      expect(agentCard.name).toBe('PostFiat Agent');
      expect(agentCard.description).toBe('A PostFiat-enabled agent');
      expect(agentCard.version).toBe('1.0.0');
      expect(agentCard.protocolVersion).toBe('1.0');
      expect(agentCard.url).toBe('https://postfiat.org');
    });

    it('should validate agent card requirements for storage', async () => {
      const request = new StoreAgentCardRequest();
      // request.agentCard is not set

      await expect(service.storeAgentCard(request)).rejects.toThrow('Agent card is required');
    });

    it('should store and retrieve agent card', async () => {
      const agentCard = new AgentCard();
      agentCard.name = 'Test Agent';
      agentCard.description = 'A test agent';
      agentCard.version = '1.0.0';

      const storeRequest = new StoreAgentCardRequest();
      storeRequest.agentCard = agentCard;
      storeRequest.agentId = 'test-agent-123';

      const storedCard = await service.storeAgentCard(storeRequest);
      
      expect(storedCard).toBeDefined();
      expect(storedCard.name).toBe('Test Agent');
      expect(storedCard.description).toBe('A test agent');
    });
  });
});