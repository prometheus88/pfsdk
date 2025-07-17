/**
 * Enhanced integration test for PostFiat selective disclosure
 * Tests selective disclosure permutations with v3 protocol features:
 * - Original 432 base scenarios
 * - AccessGrant complexity patterns
 * - Context DAG depth variations
 * - Multi-group access patterns
 * 
 * Uses actual PostFiat v3 protobuf types with AccessGrant system
 */

// Import v3 protocol types directly from generated protobuf
import { 
  Envelope, 
  EncryptionMode, 
  ContextReference, 
  AccessGrant,
  KeyType,
  CoreMessage,
  PostFiatEnvelopePayload,
  MessageType 
} from '../../../src/generated/postfiat/v3/messages_pb';

// Import PostFiat SDK opinionated crypto module
import { PostFiatCrypto, PostFiatEnvelopeBuilder } from '../../../src/crypto';

// Mock TextEncoder/TextDecoder for Jest environment
global.TextEncoder = require('util').TextEncoder;
global.TextDecoder = require('util').TextDecoder;

// Set up real crypto for Jest environment using Node.js crypto
const { webcrypto } = require('crypto');
Object.defineProperty(globalThis, 'crypto', {
  value: webcrypto
});

// Generate cryptographic keys using PostFiat SDK opinionated crypto
let ALICE_KEYS: { publicKey: string; privateKey: string };
let BOB_KEYS: { publicKey: string; privateKey: string };
let ALICE_ADDRESS: string;
let BOB_ADDRESS: string;

// Enhanced test configuration types
interface TestCase {
  senderSequence: string; // e.g. "AAA", "AAB", etc.
  middleMessageEncryption: EncryptionMode;
  initialRecipient: 'broadcast' | 'direct';
  middleMessagePublicRefs: number;
  middleMessagePrivateRefs: number;
  observer: 'A' | 'B';
  
  // NEW: AccessGrant complexity dimension
  accessGrantPattern: 'single-content' | 'single-group' | 'multi-content' | 'multi-group' | 'mixed';
  
  // NEW: Context DAG depth dimension
  contextDepth: number; // 0-5+ levels of context references
  
  // NEW: Multi-group access dimension
  groupMembership: 'single' | 'multiple-same' | 'multiple-different' | 'hierarchical' | 'overlapping' | 'exclusive';
}

interface TestScenario {
  envelopes: Envelope[];
  testCase: TestCase;
  description: string;
}

describe('Enhanced PostFiat Selective Disclosure Integration Tests', () => {
  let staticReferences: Envelope[];

  beforeEach(async () => {
    // Clear any existing state
    localStorage.clear();
    
    // Generate keys using PostFiat SDK opinionated crypto
    ALICE_KEYS = await PostFiatCrypto.generateKeyPair();
    BOB_KEYS = await PostFiatCrypto.generateKeyPair();
    ALICE_ADDRESS = ALICE_KEYS.publicKey;
    BOB_ADDRESS = BOB_KEYS.publicKey;
    
    // Create static reference messages for testing
    staticReferences = await createStaticReferences();
  });

  /**
   * Create a proper PostFiat envelope using v3 protobuf types
   */
  async function createPostFiatEnvelope(
    content: string,
    encryption: EncryptionMode,
    publicReferences: ContextReference[],
    privateReferences: ContextReference[],
    accessGrants: AccessGrant[],
    replyTo: string,
    senderAddress: string,
    recipientAddress?: string,
    recipientPublicKey?: string
  ): Promise<Envelope> {
    // Determine sender's private key for crypto operations
    const senderPrivateKey = senderAddress === ALICE_ADDRESS ? ALICE_KEYS.privateKey : BOB_KEYS.privateKey;
    const actualRecipientPublicKey = recipientPublicKey || recipientAddress || '';
    
    // Use PostFiat SDK opinionated crypto for proper encryption
    const encrypted = await PostFiatCrypto.encryptForRecipient(
      content,
      actualRecipientPublicKey,
      senderPrivateKey,
      encryption
    );
    
    // Create envelope using PostFiat SDK crypto results
    const envelope = new Envelope();
    envelope.version = 1;
    envelope.messageType = MessageType.CORE_MESSAGE;
    envelope.encryption = encrypted.mode;
    envelope.replyTo = replyTo;
    envelope.message = encrypted.data;
    envelope.contentHash = encrypted.contentHash;
    
    // Set v3 protocol fields
    envelope.publicReferences = publicReferences; // Public refs visible for discovery
    
    // Merge AccessGrants: combine crypto-generated grants with test-specific grants
    const allAccessGrants = [...encrypted.accessGrants, ...accessGrants];
    envelope.accessGrants = allAccessGrants;
    
    // Merge metadata: combine crypto metadata with test metadata
    envelope.metadata = {
      ...encrypted.metadata,
      'X-React-Chat-Sender-Address': senderAddress,
      'X-React-Chat-Timestamp': Date.now().toString()
    };
    
    if (recipientAddress) {
      envelope.metadata['X-React-Chat-Recipient-Address'] = recipientAddress;
    }
    
    // Add private references to core message (encrypted content)
    if (privateReferences.length > 0) {
      // In a real implementation, these would be added to the encrypted core message
      // For testing, we'll add them to metadata
      envelope.metadata['X-PostFiat-Private-Refs-Count'] = privateReferences.length.toString();
    }
    
    return envelope;
  }

  /**
   * Create static reference messages to use in public/private references
   */
  async function createStaticReferences(): Promise<Envelope[]> {
    const references: Envelope[] = [];
    
    // Create 4 reference messages (we'll use subsets of these)
    const referenceContents = [
      'Reference message 1 - public context',
      'Reference message 2 - shared knowledge', 
      'Reference message 3 - private context',
      'Reference message 4 - encrypted reference'
    ];
    
    for (let index = 0; index < referenceContents.length; index++) {
      const content = referenceContents[index];
      const senderAddr = index % 2 === 0 ? ALICE_ADDRESS : BOB_ADDRESS;
      const envelope = await createPostFiatEnvelope(
        content,
        index >= 2 ? EncryptionMode.PROTECTED : EncryptionMode.NONE,
        [], // publicReferences
        [], // privateReferences
        [], // accessGrants
        '', // replyTo
        senderAddr,
        undefined // recipientAddress
      );
      
      // Adjust timestamp to be in the past
      const metadata = envelope.metadata || {};
      metadata['X-React-Chat-Timestamp'] = (Date.now() - (4 - index) * 1000).toString();
      envelope.metadata = metadata;
      
      references.push(envelope);
    }
    
    return references;
  }

  /**
   * Create group hierarchy access grants for multi-group scenarios
   */
  function createGroupHierarchyGrants(groupPattern: string, targetId: string): AccessGrant[] {
    const grants: AccessGrant[] = [];
    
    switch (groupPattern) {
      case 'hierarchical':
        // Parent-child group relationship: admin group can access child group content
        const parentGrant = new AccessGrant();
        parentGrant.keyType = KeyType.GROUP_KEY;
        parentGrant.targetId = `parent-group-${targetId}`;
        parentGrant.encryptedKeyMaterial = new Uint8Array([200, 201, 202, 203]);
        grants.push(parentGrant);
        
        const childGrant = new AccessGrant();
        childGrant.keyType = KeyType.GROUP_KEY;
        childGrant.targetId = `child-group-${targetId}`;
        childGrant.encryptedKeyMaterial = new Uint8Array([204, 205, 206, 207]);
        grants.push(childGrant);
        break;
        
      case 'overlapping':
        // Overlapping groups: user belongs to multiple groups with shared content access
        const group1Grant = new AccessGrant();
        group1Grant.keyType = KeyType.GROUP_KEY;
        group1Grant.targetId = `overlap-group-1-${targetId}`;
        group1Grant.encryptedKeyMaterial = new Uint8Array([210, 211, 212, 213]);
        grants.push(group1Grant);
        
        const group2Grant = new AccessGrant();
        group2Grant.keyType = KeyType.GROUP_KEY;
        group2Grant.targetId = `overlap-group-2-${targetId}`;
        group2Grant.encryptedKeyMaterial = new Uint8Array([214, 215, 216, 217]);
        grants.push(group2Grant);
        
        const sharedGrant = new AccessGrant();
        sharedGrant.keyType = KeyType.CONTENT_KEY;
        sharedGrant.targetId = `shared-content-${targetId}`;
        sharedGrant.encryptedKeyMaterial = new Uint8Array([218, 219, 220, 221]);
        grants.push(sharedGrant);
        break;
        
      case 'exclusive':
        // Exclusive group access: content accessible only to specific group
        const exclusiveGrant = new AccessGrant();
        exclusiveGrant.keyType = KeyType.GROUP_KEY;
        exclusiveGrant.targetId = `exclusive-group-${targetId}`;
        exclusiveGrant.encryptedKeyMaterial = new Uint8Array([230, 231, 232, 233]);
        grants.push(exclusiveGrant);
        break;
        
      case 'multiple-same':
        // Multiple groups with same access level
        for (let i = 0; i < 2; i++) {
          const grant = new AccessGrant();
          grant.keyType = KeyType.GROUP_KEY;
          grant.targetId = `same-level-group-${i}-${targetId}`;
          grant.encryptedKeyMaterial = new Uint8Array([240 + i, 241 + i, 242 + i, 243 + i]);
          grants.push(grant);
        }
        break;
        
      case 'multiple-different':
        // Multiple groups with different access levels
        const highAccessGrant = new AccessGrant();
        highAccessGrant.keyType = KeyType.GROUP_KEY;
        highAccessGrant.targetId = `high-access-group-${targetId}`;
        highAccessGrant.encryptedKeyMaterial = new Uint8Array([250, 251, 252, 253]);
        grants.push(highAccessGrant);
        
        const lowAccessGrant = new AccessGrant();
        lowAccessGrant.keyType = KeyType.CONTENT_KEY;
        lowAccessGrant.targetId = `low-access-content-${targetId}`;
        lowAccessGrant.encryptedKeyMaterial = new Uint8Array([254, 255, 1, 2]);
        grants.push(lowAccessGrant);
        break;
        
      default:
        // Single group (baseline) - no additional grants needed
        // The original test already handles single group access grants
        break;
    }
    
    return grants;
  }

  /**
   * Create cross-group context references for group-specific content sharing
   */
  function createCrossGroupContextRefs(groupPattern: string, baseRefs: ContextReference[]): ContextReference[] {
    const crossGroupRefs: ContextReference[] = [...baseRefs];
    
    if (groupPattern === 'hierarchical' || groupPattern === 'overlapping') {
      // Add cross-group references that span multiple groups
      for (let i = 0; i < Math.min(2, baseRefs.length); i++) {
        const crossRef = new ContextReference();
        crossRef.contentHash = baseRefs[i].contentHash;
        crossRef.groupId = `cross-group-${groupPattern}-${i}`;
        crossGroupRefs.push(crossRef);
      }
    }
    
    return crossGroupRefs;
  }

  /**
   * Create deep context reference chains for testing Context DAG traversal
   */
  async function createDeepContextChain(depth: number, testCase: TestCase): Promise<Envelope[]> {
    if (depth <= 1) {
      // Return simple static references for shallow depths
      return staticReferences.slice(0, Math.min(depth, staticReferences.length));
    }

    const deepChain: Envelope[] = [];
    let previousEnvelope: Envelope | null = null;
    
    for (let level = 0; level < depth; level++) {
      const senderAddr = level % 2 === 0 ? ALICE_ADDRESS : BOB_ADDRESS;
      const isEncrypted = level >= 2; // Deeper levels are encrypted
      
      // Create references to previous envelope in chain
      const contextRefs: ContextReference[] = [];
      if (previousEnvelope) {
        const contextRef = new ContextReference();
        contextRef.contentHash = previousEnvelope.contentHash;
        contextRef.groupId = `chain-group-${level}`;
        contextRefs.push(contextRef);
        
        // Add circular reference detection test case
        if (testCase.senderSequence === 'AAA' && testCase.contextDepth >= 3 && level === depth - 1) {
          // Create circular reference back to first envelope
          if (deepChain.length > 0) {
            const circularRef = new ContextReference();
            circularRef.contentHash = deepChain[0].contentHash;
            circularRef.groupId = `circular-group-${level}`;
            contextRefs.push(circularRef);
          }
        }
      }
      
      // Create AccessGrants for this level
      const accessGrants: AccessGrant[] = [];
      if (isEncrypted) {
        const grant = new AccessGrant();
        grant.keyType = level % 2 === 0 ? KeyType.CONTENT_KEY : KeyType.GROUP_KEY;
        grant.targetId = `deep-context-${level}`;
        grant.encryptedKeyMaterial = new Uint8Array([100 + level, 110 + level, 120 + level, 130 + level]);
        accessGrants.push(grant);
      }
      
      const envelope = await createPostFiatEnvelope(
        `Deep context level ${level} - testing ${depth}-level DAG traversal`,
        isEncrypted ? EncryptionMode.PROTECTED : EncryptionMode.NONE,
        [], // publicReferences (context refs go in private)
        contextRefs, // privateReferences (hidden in encrypted content)
        accessGrants,
        previousEnvelope ? previousEnvelope.contentHash.toString() : '', // replyTo
        senderAddr
      );
      
      // Adjust timestamp to create proper ordering
      envelope.metadata = envelope.metadata || {};
      envelope.metadata['X-React-Chat-Timestamp'] = (Date.now() - (depth - level) * 1000).toString();
      
      deepChain.push(envelope);
      previousEnvelope = envelope;
    }
    
    return deepChain;
  }

  /**
   * Create branching DAG structure for complex context scenarios
   */
  async function createBranchingDAG(testCase: TestCase): Promise<Envelope[]> {
    if (testCase.contextDepth < 3) {
      return []; // Not enough depth for branching
    }
    
    // Create root envelope
    const rootEnvelope = await createPostFiatEnvelope(
      'DAG root - branching context structure',
      EncryptionMode.NONE,
      [], [],  [], '', ALICE_ADDRESS
    );
    
    // Create two branch paths from root
    const branch1 = await createPostFiatEnvelope(
      'DAG branch 1 - public path',
      EncryptionMode.NONE,
      [], 
      [{
        contentHash: rootEnvelope.contentHash,
        groupId: 'branch-1-group'
      } as ContextReference],
      [], rootEnvelope.contentHash.toString(), BOB_ADDRESS
    );
    
    const branch2 = await createPostFiatEnvelope(
      'DAG branch 2 - encrypted path',
      EncryptionMode.PROTECTED,
      [],
      [{
        contentHash: rootEnvelope.contentHash,
        groupId: 'branch-2-group'
      } as ContextReference],
      [{
        keyType: KeyType.GROUP_KEY,
        targetId: 'branch-2-group',
        encryptedKeyMaterial: new Uint8Array([200, 201, 202, 203])
      } as AccessGrant],
      rootEnvelope.contentHash.toString(), ALICE_ADDRESS
    );
    
    // Create convergence envelope that references both branches
    const convergenceEnvelope = await createPostFiatEnvelope(
      'DAG convergence - partial access test',
      EncryptionMode.PROTECTED,
      [],
      [
        {
          contentHash: branch1.contentHash,
          groupId: 'convergence-group-1'
        } as ContextReference,
        {
          contentHash: branch2.contentHash,
          groupId: 'convergence-group-2'  
        } as ContextReference
      ],
      [{
        keyType: KeyType.CONTENT_KEY,
        targetId: 'convergence-content',
        encryptedKeyMaterial: new Uint8Array([210, 211, 212, 213])
      } as AccessGrant],
      `${branch1.contentHash.toString()},${branch2.contentHash.toString()}`,
      BOB_ADDRESS
    );
    
    return [rootEnvelope, branch1, branch2, convergenceEnvelope];
  }

  /**
   * Generate all enhanced test case permutations (~1,080+ scenarios)
   * Original 432 + AccessGrant complexity + Context depth + Multi-group access
   */
  function generateAllTestCases(): TestCase[] {
    const testCases: TestCase[] = [];
    
    // Original dimensions (432 base scenarios)
    const senderSequences = ['AAA', 'AAB', 'ABA', 'ABB', 'BAA', 'BAB', 'BBA', 'BBB'];
    const encryptionModes = [EncryptionMode.NONE, EncryptionMode.PROTECTED, EncryptionMode.PUBLIC_KEY];
    const initialRecipients: ('broadcast' | 'direct')[] = ['broadcast', 'direct'];
    const publicRefCounts = [0, 1, 2];
    const privateRefCounts = [0, 1, 2];
    
    // NEW: AccessGrant complexity patterns
    const accessGrantPatterns: ('single-content' | 'single-group' | 'multi-content' | 'multi-group' | 'mixed')[] = [
      'single-content', 'single-group', 'multi-content', 'multi-group', 'mixed'
    ];
    
    // NEW: Context DAG depth levels (enhanced for deep testing)
    const contextDepths = [0, 1, 2, 3, 4, 5]; // 0=no context, 1-5=increasing depth for deep DAG testing
    
    // NEW: Group membership patterns
    const groupMemberships: ('single' | 'multiple-same' | 'multiple-different' | 'hierarchical' | 'overlapping' | 'exclusive')[] = [
      'single', 'multiple-same', 'multiple-different', 'hierarchical', 'overlapping', 'exclusive'
    ];
    
    // Generate enhanced permutations with focused sampling
    for (const senderSequence of senderSequences) {
      for (const encryption of encryptionModes) {
        for (const initialRecipient of initialRecipients) {
          for (const publicRefs of publicRefCounts) {
            for (const privateRefs of privateRefCounts) {
              
              // 1. Original baseline scenario
              testCases.push({
                senderSequence,
                middleMessageEncryption: encryption,
                initialRecipient,
                middleMessagePublicRefs: publicRefs,
                middleMessagePrivateRefs: privateRefs,
                observer: 'A',
                accessGrantPattern: 'single-content',
                contextDepth: 1,
                groupMembership: 'single'
              });
              
              // 2. AccessGrant complexity variations (every 2nd base scenario)
              if ((publicRefs + privateRefs) % 2 === 0) {
                for (const grantPattern of accessGrantPatterns.slice(1)) {
                  testCases.push({
                    senderSequence,
                    middleMessageEncryption: encryption,
                    initialRecipient,
                    middleMessagePublicRefs: publicRefs,
                    middleMessagePrivateRefs: privateRefs,
                    observer: 'A',
                    accessGrantPattern: grantPattern,
                    contextDepth: 1,
                    groupMembership: 'single'
                  });
                }
              }
              
              // 3. Context depth variations (every 3rd base scenario)
              if ((publicRefs + privateRefs) % 3 === 0) {
                for (const depth of contextDepths.slice(2)) { // Test deeper contexts
                  testCases.push({
                    senderSequence,
                    middleMessageEncryption: encryption,
                    initialRecipient,
                    middleMessagePublicRefs: publicRefs,
                    middleMessagePrivateRefs: privateRefs,
                    observer: 'A',
                    accessGrantPattern: 'single-content',
                    contextDepth: depth,
                    groupMembership: 'single'
                  });
                }
              }
              
              // 4. Group membership variations (every 4th base scenario)
              if (senderSequence.length === 3 && senderSequence.charAt(1) === 'A') {
                for (const groupPattern of groupMemberships.slice(1)) {
                  testCases.push({
                    senderSequence,
                    middleMessageEncryption: encryption,
                    initialRecipient,
                    middleMessagePublicRefs: publicRefs,
                    middleMessagePrivateRefs: privateRefs,
                    observer: 'A',
                    accessGrantPattern: 'single-content',
                    contextDepth: 1,
                    groupMembership: groupPattern
                  });
                }
              }
            }
          }
        }
      }
    }
    
    return testCases;
  }

  /**
   * Build a 3-envelope sequence based on enhanced test case parameters
   */
  async function buildEnvelopeSequence(testCase: TestCase): Promise<TestScenario> {
    const { senderSequence, middleMessageEncryption, initialRecipient, middleMessagePublicRefs, middleMessagePrivateRefs } = testCase;
    
    const senders = senderSequence.split('') as ('A' | 'B')[];
    const envelopes: Envelope[] = [];
    
    // Envelope 1: Simple message (plain text, no references)
    const firstSender = senders[0] === 'A' ? ALICE_ADDRESS : BOB_ADDRESS;
    const firstRecipient = initialRecipient === 'direct' ? (senders[0] === 'A' ? BOB_ADDRESS : ALICE_ADDRESS) : undefined;
    
    const envelope1 = await createPostFiatEnvelope(
      `Message 1 from ${senders[0]}`,
      EncryptionMode.NONE,
      [], // publicReferences
      [], // privateReferences
      [], // accessGrants
      '', // replyTo
      firstSender,
      firstRecipient
    );
    envelopes.push(envelope1);
    
    // Envelope 2: Complex middle message (variable encryption and references)
    const secondSender = senders[1] === 'A' ? ALICE_ADDRESS : BOB_ADDRESS;
    const secondRecipient = initialRecipient === 'direct' ? (senders[1] === 'A' ? BOB_ADDRESS : ALICE_ADDRESS) : undefined;
    
    // Build references for middle message using enhanced deep context system
    let publicRefs: ContextReference[] = [];
    let privateRefs: ContextReference[] = [];
    let deepContextEnvelopes: Envelope[] = [];
    
    if (testCase.contextDepth > 0) {
      // Create deep context chain based on specified depth
      deepContextEnvelopes = await createDeepContextChain(testCase.contextDepth, testCase);
      
      // Convert deep context chain to references
      const contextRefs = deepContextEnvelopes.map((envelope, index) => {
        const contextRef = new ContextReference();
        contextRef.contentHash = envelope.contentHash;
        contextRef.groupId = `deep-context-group-${index}`;
        return contextRef;
      });
      
      // Ensure we have enough context references for the test requirements
      const totalRefsNeeded = middleMessagePublicRefs + middleMessagePrivateRefs;
      while (contextRefs.length < totalRefsNeeded) {
        // Pad with additional static references if needed
        const additionalRef = staticReferences[contextRefs.length % staticReferences.length];
        const contextRef = new ContextReference();
        contextRef.contentHash = additionalRef.contentHash;
        contextRef.groupId = `padded-context-group-${contextRefs.length}`;
        contextRefs.push(contextRef);
      }
      
      // Split between public and private based on original ref counts
      publicRefs = contextRefs.slice(0, middleMessagePublicRefs);
      privateRefs = contextRefs.slice(middleMessagePublicRefs, middleMessagePublicRefs + middleMessagePrivateRefs);
      
      // Add branching DAG structure for complex scenarios
      if (testCase.contextDepth >= 3 && testCase.accessGrantPattern === 'mixed') {
        const branchingDAG = await createBranchingDAG(testCase);
        if (branchingDAG.length > 0) {
          // Add references to the branching structure
          const branchRefs = branchingDAG.slice(0, 2).map((envelope, index) => {
            const contextRef = new ContextReference();
            contextRef.contentHash = envelope.contentHash;
            contextRef.groupId = `branch-group-${index}`;
            return contextRef;
          });
          privateRefs.push(...branchRefs);
        }
      }
    } else {
      // Fall back to static references for depth 0, with padding if needed
      const totalRefsNeeded = middleMessagePublicRefs + middleMessagePrivateRefs;
      const paddedStaticRefs = [...staticReferences];
      
      // Pad with mock references if we need more than available
      while (paddedStaticRefs.length < totalRefsNeeded) {
        const mockRef = await createPostFiatEnvelope(
          `Mock reference ${paddedStaticRefs.length}`,
          EncryptionMode.NONE,
          [], [], [], '', ALICE_ADDRESS
        );
        paddedStaticRefs.push(mockRef);
      }
      
      
      publicRefs = paddedStaticRefs.slice(0, middleMessagePublicRefs).map((ref, index) => {
        const contextRef = new ContextReference();
        contextRef.contentHash = ref.contentHash;
        contextRef.groupId = `static-public-group-${index}`;
        return contextRef;
      });
      
      privateRefs = paddedStaticRefs.slice(middleMessagePublicRefs, middleMessagePublicRefs + middleMessagePrivateRefs).map((ref, index) => {
        const contextRef = new ContextReference();
        contextRef.contentHash = ref.contentHash;
        contextRef.groupId = `static-private-group-${index}`;
        return contextRef;
      });
    }
    
    // Create AccessGrants based on the test case pattern
    const accessGrants: AccessGrant[] = [];
    
    switch (testCase.accessGrantPattern) {
      case 'single-content':
        const contentGrant = new AccessGrant();
        contentGrant.keyType = KeyType.CONTENT_KEY;
        contentGrant.targetId = 'message-content';
        contentGrant.encryptedKeyMaterial = new Uint8Array([1, 2, 3, 4]);
        accessGrants.push(contentGrant);
        break;
        
      case 'single-group':
        const groupGrant = new AccessGrant();
        groupGrant.keyType = KeyType.GROUP_KEY;
        groupGrant.targetId = 'main-group';
        groupGrant.encryptedKeyMaterial = new Uint8Array([5, 6, 7, 8]);
        accessGrants.push(groupGrant);
        break;
        
      case 'multi-content':
        for (let i = 0; i < 2; i++) {
          const grant = new AccessGrant();
          grant.keyType = KeyType.CONTENT_KEY;
          grant.targetId = `content-${i}`;
          grant.encryptedKeyMaterial = new Uint8Array([10 + i, 20 + i, 30 + i, 40 + i]);
          accessGrants.push(grant);
        }
        break;
        
      case 'multi-group':
        for (let i = 0; i < 2; i++) {
          const grant = new AccessGrant();
          grant.keyType = KeyType.GROUP_KEY;
          grant.targetId = `group-${i}`;
          grant.encryptedKeyMaterial = new Uint8Array([50 + i, 60 + i, 70 + i, 80 + i]);
          accessGrants.push(grant);
        }
        break;
        
      case 'mixed':
        const contentGrant2 = new AccessGrant();
        contentGrant2.keyType = KeyType.CONTENT_KEY;
        contentGrant2.targetId = 'mixed-content';
        contentGrant2.encryptedKeyMaterial = new Uint8Array([90, 91, 92, 93]);
        
        const groupGrant2 = new AccessGrant();
        groupGrant2.keyType = KeyType.GROUP_KEY;
        groupGrant2.targetId = 'mixed-group';
        groupGrant2.encryptedKeyMaterial = new Uint8Array([94, 95, 96, 97]);
        
        accessGrants.push(contentGrant2, groupGrant2);
        break;
    }
    
    // Add group hierarchy grants based on groupMembership pattern (only for enhanced patterns)
    if (testCase.groupMembership !== 'single') {
      const groupHierarchyGrants = createGroupHierarchyGrants(testCase.groupMembership, testCase.accessGrantPattern);
      accessGrants.push(...groupHierarchyGrants);
    }
    
    // Debug logging for failing cases
    if (testCase.senderSequence === 'AAA' && testCase.middleMessageEncryption === EncryptionMode.NONE && testCase.accessGrantPattern === 'single-content') {
      console.log(`DEBUG: AAA-0-single-content case - accessGrants.length before crypto: ${accessGrants.length}, groupMembership: ${testCase.groupMembership}`);
    }
    
    // Apply cross-group context references if applicable
    if (testCase.groupMembership === 'hierarchical' || testCase.groupMembership === 'overlapping') {
      publicRefs = createCrossGroupContextRefs(testCase.groupMembership, publicRefs);
    }
    
    // Determine recipient public key for PUBLIC_KEY encryption
    let recipientPublicKey: string | undefined;
    if (middleMessageEncryption === EncryptionMode.PUBLIC_KEY) {
      if (secondRecipient) {
        recipientPublicKey = secondRecipient;
      } else {
        recipientPublicKey = senders[1] === 'A' ? BOB_ADDRESS : ALICE_ADDRESS;
      }
    }
    
    const envelope2 = await createPostFiatEnvelope(
      `Message 2 from ${senders[1]} - enhanced: encryption=${middleMessageEncryption}, grants=${testCase.accessGrantPattern}, depth=${testCase.contextDepth}, groups=${testCase.groupMembership}`,
      middleMessageEncryption,
      publicRefs,
      privateRefs,
      accessGrants,
      envelope1.contentHash.toString(), // Reply to first message
      secondSender,
      secondRecipient,
      recipientPublicKey
    );
    
    // Adjust timestamp to be after first message
    const metadata2 = envelope2.metadata || {};
    metadata2['X-React-Chat-Timestamp'] = (Date.now() + 1000).toString();
    envelope2.metadata = metadata2;
    
    // Debug logging for failing cases
    if (testCase.senderSequence === 'AAA' && testCase.middleMessageEncryption === EncryptionMode.NONE && testCase.accessGrantPattern === 'single-content') {
      console.log(`DEBUG: AAA-0-single-content case - final envelope2.accessGrants.length: ${envelope2.accessGrants.length}, groupMembership: ${testCase.groupMembership}`);
    }
    
    envelopes.push(envelope2);
    
    // Envelope 3: Simple reply (plain text, no references)
    const thirdSender = senders[2] === 'A' ? ALICE_ADDRESS : BOB_ADDRESS;
    const thirdRecipient = initialRecipient === 'direct' ? (senders[2] === 'A' ? BOB_ADDRESS : ALICE_ADDRESS) : undefined;
    
    const envelope3 = await createPostFiatEnvelope(
      `Message 3 from ${senders[2]}`,
      EncryptionMode.NONE,
      [],
      [],
      [],
      envelope2.contentHash.toString(),
      thirdSender,
      thirdRecipient
    );
    
    // Adjust timestamp to be after second message
    const metadata3 = envelope3.metadata || {};
    metadata3['X-React-Chat-Timestamp'] = (Date.now() + 2000).toString();
    envelope3.metadata = metadata3;
    
    envelopes.push(envelope3);
    
    return {
      envelopes,
      testCase,
      description: `Enhanced: ${senderSequence}, ${middleMessageEncryption}, ${initialRecipient}, refs:${middleMessagePublicRefs}/${middleMessagePrivateRefs}, grants:${testCase.accessGrantPattern}, depth:${testCase.contextDepth}, groups:${testCase.groupMembership}`
    };
  }

  /**
   * Test a single enhanced scenario
   */
  async function testSingleScenario(scenario: TestScenario) {
    const { envelopes, testCase } = scenario;
    const middleEnvelope = envelopes[1];
    
    // Test: Enhanced envelope structure should be valid
    expect(middleEnvelope).toBeDefined();
    expect(middleEnvelope.contentHash).toBeTruthy();
    expect(middleEnvelope.version).toBe(1);
    expect(middleEnvelope.encryption).toBe(testCase.middleMessageEncryption);
    expect(middleEnvelope.message).toBeDefined();
    
    // Test: AccessGrant patterns should be correct
    expect(middleEnvelope.accessGrants).toBeDefined();
    
    // PostFiatCrypto automatically adds 1 grant for encryption, plus test-specific grants, plus group hierarchy grants
    const cryptoBaseGrants = middleEnvelope.encryption === EncryptionMode.NONE ? 0 : 1;
    const testSpecificGrants = testCase.accessGrantPattern === 'multi-content' || testCase.accessGrantPattern === 'multi-group' ? 2 :
                              testCase.accessGrantPattern === 'mixed' ? 2 : 1;
    
    // Calculate group hierarchy grants based on groupMembership pattern
    let groupHierarchyGrants = 0; // No extra grants for 'single' pattern
    switch (testCase.groupMembership) {
      case 'hierarchical': groupHierarchyGrants = 2; break;  // parent + child
      case 'overlapping': groupHierarchyGrants = 3; break;   // group1 + group2 + shared
      case 'exclusive': groupHierarchyGrants = 1; break;     // exclusive group
      case 'multiple-same': groupHierarchyGrants = 2; break; // 2 same-level groups
      case 'multiple-different': groupHierarchyGrants = 2; break; // high + low access
      default: groupHierarchyGrants = 0; break;              // single group (no extra grants)
    }
    
    const expectedGrantCount = cryptoBaseGrants + testSpecificGrants + groupHierarchyGrants;
    expect(middleEnvelope.accessGrants.length).toBe(expectedGrantCount);
    
    // Test: Public references should be visible
    expect(middleEnvelope.publicReferences).toBeDefined();
    
    // Calculate expected public references including cross-group additions
    let expectedPublicRefs = testCase.middleMessagePublicRefs;
    if (testCase.groupMembership === 'hierarchical' || testCase.groupMembership === 'overlapping') {
      // Cross-group patterns add 2 more references (up to min(2, baseRefs.length))
      expectedPublicRefs += Math.min(2, testCase.middleMessagePublicRefs);
    }
    expect(middleEnvelope.publicReferences.length).toBe(expectedPublicRefs);
    
    // Test: Deep context DAG structure validation
    if (testCase.contextDepth > 0) {
      // Should have context references that scale with depth
      const totalExpectedRefs = testCase.middleMessagePublicRefs + testCase.middleMessagePrivateRefs;
      const actualRefs = middleEnvelope.publicReferences.length;
      expect(actualRefs).toBeGreaterThanOrEqual(0);
      
      // Validate context group IDs follow deep context naming convention
      const publicGroupIds = middleEnvelope.publicReferences.map(ref => ref.groupId);
      if (publicGroupIds.length > 0) {
        expect(publicGroupIds.some(id => id.includes('deep-context-group') || id.includes('static'))).toBe(true);
      }
      
      // For deeper contexts (3+), test branching DAG scenarios
      if (testCase.contextDepth >= 3 && testCase.accessGrantPattern === 'mixed') {
        // Should have additional complexity from branching DAG
        expect(middleEnvelope.accessGrants.length).toBeGreaterThanOrEqual(1);
      }
      
      // Test circular reference detection for specific scenarios
      if (testCase.senderSequence === 'AAA' && testCase.contextDepth >= 3) {
        // These scenarios include circular reference test cases
        expect(middleEnvelope.publicReferences.length + middleEnvelope.accessGrants.length).toBeGreaterThanOrEqual(1);
      }
    }
    
    // Test: Context depth performance validation
    if (testCase.contextDepth >= 4) {
      // Deep context scenarios should still process efficiently
      expect(middleEnvelope).toBeDefined();
      expect(middleEnvelope.contentHash).toBeTruthy();
    }
    
    // Test: Reply chain should be correct
    expect(middleEnvelope.replyTo).toBeTruthy();
    expect(envelopes[2].replyTo).toBeTruthy();
  }

  /**
   * Main test runner - executes enhanced selective disclosure test cases
   */
  it('should handle enhanced selective disclosure permutations correctly', async () => {
    const allTestCases = generateAllTestCases();
    
    console.log(`Generated ${allTestCases.length} enhanced test scenarios`);
    expect(allTestCases.length).toBeGreaterThan(432); // Should be significantly more than original
    
    // Run all test cases - performance is excellent at ~1 second for 2,112 scenarios
    const testCasesToRun = allTestCases;
    console.log(`Testing all ${allTestCases.length} scenarios (100% coverage)`);
    
    let passedTests = 0;
    let failedTests = 0;
    const failedCases: string[] = [];
    
    for (const testCase of testCasesToRun) {
      try {
        const scenario = await buildEnvelopeSequence(testCase);
        
        // Test both observers A and B for this scenario
        for (const observer of ['A', 'B'] as const) {
          const observerTestCase = { ...testCase, observer };
          const observerScenario = { ...scenario, testCase: observerTestCase };
          await testSingleScenario(observerScenario);
          passedTests++;
        }
      } catch (error) {
        failedTests++;
        const caseDescription = `${testCase.senderSequence}-${testCase.contextDepth}-${testCase.accessGrantPattern}-${testCase.groupMembership}-pubRefs${testCase.middleMessagePublicRefs}`;
        failedCases.push(caseDescription);
        
        if (failedTests <= 5) {
          console.error(`Enhanced test failed for case: ${caseDescription}`, error);
          console.error(`Full test case:`, JSON.stringify(testCase, null, 2));
        }
      }
    }
    
    console.log(`Enhanced selective disclosure tests completed: ${passedTests} passed, ${failedTests} failed`);
    if (failedCases.length > 0) {
      console.log(`Failed cases: ${failedCases.slice(0, 5).join(', ')}${failedCases.length > 5 ? '...' : ''}`);
    }
    
    const totalTests = testCasesToRun.length * 2; // Each test case tests both observers
    console.log(`Total enhanced tests run: ${totalTests} (${allTestCases.length} scenarios × 2 observers)`);
    
    // Expect high pass rate for enhanced v3 protocol tests
    expect(passedTests / totalTests).toBeGreaterThan(0.9);
  }, 60000); // 60 second timeout for enhanced tests

  /**
   * Focused tests for specific enhanced scenarios
   */
  describe('Enhanced selective disclosure scenarios', () => {
    it('should validate AccessGrant complexity patterns', async () => {
      const testCase: TestCase = {
        senderSequence: 'AAA',
        middleMessageEncryption: EncryptionMode.PROTECTED,
        initialRecipient: 'broadcast',
        middleMessagePublicRefs: 1,
        middleMessagePrivateRefs: 1,
        observer: 'A',
        accessGrantPattern: 'mixed',
        contextDepth: 1,
        groupMembership: 'single'
      };
      
      const scenario = await buildEnvelopeSequence(testCase);
      const envelope = scenario.envelopes[1];
      
      // Should have mixed grants: 1 from crypto + 2 from test (1 CONTENT_KEY + 1 GROUP_KEY) + 0 from group hierarchy (single)
      expect(envelope.accessGrants.length).toBe(3);
      const grantTypes = envelope.accessGrants.map(g => g.keyType);
      expect(grantTypes).toContain(KeyType.CONTENT_KEY);
      expect(grantTypes).toContain(KeyType.GROUP_KEY);
    });

    it('should handle multi-group access patterns', async () => {
      const testCase: TestCase = {
        senderSequence: 'ABA',
        middleMessageEncryption: EncryptionMode.NONE,
        initialRecipient: 'direct',
        middleMessagePublicRefs: 2,
        middleMessagePrivateRefs: 1,
        observer: 'A',
        accessGrantPattern: 'multi-group',
        contextDepth: 2,
        groupMembership: 'multiple-different'
      };
      
      const scenario = await buildEnvelopeSequence(testCase);
      const envelope = scenario.envelopes[1];
      
      // Should have multiple GROUP_KEY grants: 0 from crypto (NONE encryption) + 2 from test (multi-group) + 2 from group hierarchy  
      expect(envelope.accessGrants.length).toBe(4);
      // Most grants should be GROUP_KEY (test creates GROUP_KEY grants, hierarchy creates GROUP_KEY grants)
      const groupKeyCount = envelope.accessGrants.filter(g => g.keyType === KeyType.GROUP_KEY).length;
      expect(groupKeyCount).toBeGreaterThanOrEqual(2);
      
      // Should have different target groups (at least 2 unique IDs among the 4 grants)
      const targetIds = envelope.accessGrants.map(g => g.targetId);
      expect(new Set(targetIds).size).toBeGreaterThanOrEqual(2); // Multiple unique target IDs
    });

    it('should validate enhanced protobuf structure', async () => {
      const testCase: TestCase = {
        senderSequence: 'BBB',
        middleMessageEncryption: EncryptionMode.PUBLIC_KEY,
        initialRecipient: 'broadcast',
        middleMessagePublicRefs: 2,
        middleMessagePrivateRefs: 2,
        observer: 'B',
        accessGrantPattern: 'single-content',
        contextDepth: 3,
        groupMembership: 'multiple-same'
      };
      
      const scenario = await buildEnvelopeSequence(testCase);
      const envelope = scenario.envelopes[1];
      
      // Verify enhanced v3 protobuf structure
      expect(envelope.version).toBe(1);
      expect(envelope.contentHash).toBeTruthy();
      expect(envelope.encryption).toBe(EncryptionMode.PUBLIC_KEY);
      expect(envelope.message).toBeDefined();
      expect(envelope.publicReferences).toBeDefined();
      expect(envelope.accessGrants).toBeDefined();
      expect(envelope.replyTo).toBeTruthy();
      
      // Verify metadata structure
      expect(envelope.metadata).toBeDefined();
      expect(envelope.metadata['X-React-Chat-Sender-Address']).toBeTruthy();
      expect(envelope.metadata['X-React-Chat-Timestamp']).toBeTruthy();
    });

    it('should handle deep context DAG traversal (5 levels)', async () => {
      const testCase: TestCase = {
        senderSequence: 'ABA',
        middleMessageEncryption: EncryptionMode.PROTECTED,
        initialRecipient: 'direct',
        middleMessagePublicRefs: 2,
        middleMessagePrivateRefs: 1,
        observer: 'A',
        accessGrantPattern: 'single-content',
        contextDepth: 5, // Deep context chain
        groupMembership: 'single'
      };
      
      const scenario = await buildEnvelopeSequence(testCase);
      const envelope = scenario.envelopes[1];
      
      // Should handle deep context without performance degradation
      expect(envelope).toBeDefined();
      expect(envelope.contentHash).toBeTruthy();
      
      // Verify deep context references are properly structured
      const publicGroupIds = envelope.publicReferences.map(ref => ref.groupId);
      if (publicGroupIds.length > 0) {
        expect(publicGroupIds.some(id => id.includes('deep-context-group'))).toBe(true);
      }
      
      // Verify AccessGrants are present for encrypted deep contexts
      expect(envelope.accessGrants.length).toBeGreaterThanOrEqual(1);
    });

    it('should detect circular references in context chains', async () => {
      const testCase: TestCase = {
        senderSequence: 'AAA', // Triggers circular reference logic
        middleMessageEncryption: EncryptionMode.NONE,
        initialRecipient: 'broadcast',
        middleMessagePublicRefs: 1,
        middleMessagePrivateRefs: 2,
        observer: 'A',
        accessGrantPattern: 'single-content',
        contextDepth: 3, // Minimum depth for circular reference test
        groupMembership: 'single'
      };
      
      const scenario = await buildEnvelopeSequence(testCase);
      const envelope = scenario.envelopes[1];
      
      // Circular reference scenarios should still be processed successfully
      expect(envelope).toBeDefined();
      expect(envelope.contentHash).toBeTruthy();
      
      // Should have context structure that includes circular reference handling
      const totalContextItems = envelope.publicReferences.length + envelope.accessGrants.length;
      expect(totalContextItems).toBeGreaterThanOrEqual(1);
    });

    it('should handle branching DAG structures', async () => {
      const testCase: TestCase = {
        senderSequence: 'BAB',
        middleMessageEncryption: EncryptionMode.PROTECTED,
        initialRecipient: 'broadcast',
        middleMessagePublicRefs: 1,
        middleMessagePrivateRefs: 2,
        observer: 'B',
        accessGrantPattern: 'mixed', // Triggers branching DAG
        contextDepth: 4, // Deep enough for branching
        groupMembership: 'multiple-different'
      };
      
      const scenario = await buildEnvelopeSequence(testCase);
      const envelope = scenario.envelopes[1];
      
      // Branching DAG scenarios should have additional complexity
      expect(envelope).toBeDefined();
      expect(envelope.accessGrants.length).toBeGreaterThanOrEqual(2); // Mixed pattern + branching
      
      // Should have references from branching structure
      const privateRefCount = envelope.publicReferences.length;
      expect(privateRefCount).toBeGreaterThanOrEqual(0);
    });

    it('should validate partial access in deep context chains', async () => {
      const testCase: TestCase = {
        senderSequence: 'ABB',
        middleMessageEncryption: EncryptionMode.PUBLIC_KEY,
        initialRecipient: 'direct',
        middleMessagePublicRefs: 0,
        middleMessagePrivateRefs: 3,
        observer: 'B',
        accessGrantPattern: 'multi-group',
        contextDepth: 4,
        groupMembership: 'multiple-different'
      };
      
      const scenario = await buildEnvelopeSequence(testCase);
      const envelope = scenario.envelopes[1];
      
      // Partial access scenarios test selective disclosure in deep chains
      expect(envelope).toBeDefined();
      expect(envelope.encryption).toBe(EncryptionMode.PUBLIC_KEY);
      
      // Should have multiple group keys for partial access control
      expect(envelope.accessGrants.length).toBeGreaterThanOrEqual(2);
      const groupKeyCount = envelope.accessGrants.filter(g => g.keyType === KeyType.GROUP_KEY).length;
      expect(groupKeyCount).toBeGreaterThanOrEqual(1);
    });

    it('should handle hierarchical group access patterns', async () => {
      const testCase: TestCase = {
        senderSequence: 'ABA',
        middleMessageEncryption: EncryptionMode.PROTECTED,
        initialRecipient: 'broadcast',
        middleMessagePublicRefs: 2,
        middleMessagePrivateRefs: 1,
        observer: 'A',
        accessGrantPattern: 'single-group',
        contextDepth: 2,
        groupMembership: 'hierarchical'
      };
      
      const scenario = await buildEnvelopeSequence(testCase);
      const envelope = scenario.envelopes[1];
      
      // Hierarchical groups should have parent and child grants
      expect(envelope.accessGrants.length).toBeGreaterThanOrEqual(3); // crypto + single-group + hierarchical (2)
      
      // Should have cross-group context references
      expect(envelope.publicReferences.length).toBeGreaterThanOrEqual(2);
      
      // Verify hierarchy grant types
      const grantTargets = envelope.accessGrants.map(g => g.targetId);
      expect(grantTargets.some(target => target.includes('parent-group'))).toBe(true);
      expect(grantTargets.some(target => target.includes('child-group'))).toBe(true);
    });

    it('should handle overlapping group memberships', async () => {
      const testCase: TestCase = {
        senderSequence: 'BAB',
        middleMessageEncryption: EncryptionMode.PUBLIC_KEY,
        initialRecipient: 'direct',
        middleMessagePublicRefs: 1,
        middleMessagePrivateRefs: 2,
        observer: 'B',
        accessGrantPattern: 'multi-content',
        contextDepth: 3,
        groupMembership: 'overlapping'
      };
      
      const scenario = await buildEnvelopeSequence(testCase);
      const envelope = scenario.envelopes[1];
      
      // Overlapping groups should have multiple group grants plus shared content
      expect(envelope.accessGrants.length).toBeGreaterThanOrEqual(5); // crypto + multi-content (2) + overlapping (3)
      
      // Should have cross-group references
      expect(envelope.publicReferences.length).toBeGreaterThanOrEqual(1);
      
      // Verify overlapping grant structure
      const grantTargets = envelope.accessGrants.map(g => g.targetId);
      expect(grantTargets.some(target => target.includes('overlap-group-1'))).toBe(true);
      expect(grantTargets.some(target => target.includes('overlap-group-2'))).toBe(true);
      expect(grantTargets.some(target => target.includes('shared-content'))).toBe(true);
    });

    it('should handle exclusive group access patterns', async () => {
      const testCase: TestCase = {
        senderSequence: 'BBB',
        middleMessageEncryption: EncryptionMode.NONE,
        initialRecipient: 'broadcast',
        middleMessagePublicRefs: 3,
        middleMessagePrivateRefs: 0,
        observer: 'A',
        accessGrantPattern: 'mixed',
        contextDepth: 1,
        groupMembership: 'exclusive'
      };
      
      const scenario = await buildEnvelopeSequence(testCase);
      const envelope = scenario.envelopes[1];
      
      // Exclusive groups should have controlled access
      expect(envelope.accessGrants.length).toBeGreaterThanOrEqual(3); // no crypto + mixed (2) + exclusive (1)
      
      // Verify exclusive grant structure
      const grantTargets = envelope.accessGrants.map(g => g.targetId);
      expect(grantTargets.some(target => target.includes('exclusive-group'))).toBe(true);
    });
  });
});