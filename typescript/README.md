# PostFiat TypeScript SDK

Modern TypeScript SDK for the PostFiat Wallet Protocol, built with gRPC-Web and React support.

## Installation

```bash
npm install @postfiat/sdk
```

## Quick Start

### Basic Usage

```typescript
import { PostFiatClient, createConfig } from '@postfiat/sdk';

// Create a client
const client = new PostFiatClient(createConfig('development', {
  apiKey: 'your-api-key'
}));

// Use the client
const health = await client.health();
console.log(health);
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