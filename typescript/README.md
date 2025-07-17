# PostFiat TypeScript SDK

TypeScript SDK for the PostFiat Wallet Protocol, featuring KEK-CEK hierarchical group key management.

## Installation

```bash
npm install @postfiat/sdk
```

## Webpack/React Compatibility

**✅ Recommended:** Always import from the main SDK package:
```typescript
import { AccessGrant, KeyType, Envelope } from '@postfiat/sdk';
```

**❌ Avoid:** Direct protobuf imports that can cause webpack issues:
```typescript
// Don't do this - causes "Unexpected token" errors
import { AccessGrant } from '@postfiat/sdk/src/generated/postfiat/v3/messages_pb';
```

## Quick Start

### KEK-CEK Key Management

```typescript
import { AccessGrant, KeyType, ContextReference } from '@postfiat/sdk';

// Create a group key grant (encrypted with user's public key)
const groupKeyGrant = new AccessGrant({
  keyType: KeyType.GROUP_KEY,
  targetId: "research_group_xyz",
  encryptedKeyMaterial: encryptedGroupKey
});

// Create a content key grant (encrypted with group key)
const contentKeyGrant = new AccessGrant({
  keyType: KeyType.CONTENT_KEY,
  targetId: "document_hash_456",
  encryptedKeyMaterial: encryptedContentKey
});

// Context reference now uses group_id instead of decryption_key
const contextRef = new ContextReference({
  contentHash: documentHash,
  groupId: "research_group_xyz"
});
```

### React Integration

```tsx
import { PostFiatProvider, usePostFiatClient } from '@postfiat/sdk';

function App() {
  const config = createConfig('development', {
    apiKey: 'your-api-key'
  });

  return (
    <PostFiatProvider config={config}>
      <WalletComponent />
    </PostFiatProvider>
  );
}

function WalletComponent() {
  const { client } = usePostFiatClient();
  
  // Use client in your component
  return <div>Wallet Component</div>;
}
```

## Configuration

The SDK supports multiple environments:

- `local` - http://localhost:8080
- `development` - https://api-dev.postfiat.com  
- `staging` - https://api-staging.postfiat.com
- `production` - https://api.postfiat.com

## Development

### Setup

```bash
npm install
```

### Build

```bash
npm run build
```

### Test

```bash
npm test
```

### Generate Protocol Buffers

```bash
npm run generate
```

## License

MIT