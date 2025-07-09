/**
 * Auto-generated React hooks for PostFiat SDK.
 *
 * DO NOT EDIT - This file is auto-generated from proto files.
 * Run 'npm run generate:types' to regenerate.
 */

import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { PostFiatClient, ClientConfig } from '../client/base';
import { PostFiatError } from '../types/exceptions';

/**
 * PostFiat client context
 */
export const PostFiatClientContext = createContext<PostFiatClient | null>(null);

/**
 * PostFiat client provider props
 */
export interface PostFiatClientProviderProps {
  config: ClientConfig;
  children: React.ReactNode;
}

/**
 * PostFiat client provider component
 */
export function PostFiatClientProvider({ config, children }: PostFiatClientProviderProps) {
  const [client] = useState(() => new PostFiatClient(config));

  return (
    <PostFiatClientContext.Provider value={client}>
      {children}
    </PostFiatClientContext.Provider>
  );
}

/**
 * Hook to get the PostFiat client
 */
export function usePostFiatClient(): PostFiatClient {
  const client = useContext(PostFiatClientContext);
  if (!client) {
    throw new Error('usePostFiatClient must be used within a PostFiatClientProvider');
  }
  return client;
}

/**
 * State for async operations
 */
export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: PostFiatError | null;
}

/**
 * Hook for async operations with loading and error states
 */
export function useAsyncOperation<T>(): [
  AsyncState<T>,
  (operation: () => Promise<T>) => Promise<void>
] {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: false,
    error: null
  });

  const execute = useCallback(async (operation: () => Promise<T>) => {
    setState({ data: null, loading: true, error: null });
    try {
      const result = await operation();
      setState({ data: result, loading: false, error: null });
    } catch (error) {
      const postFiatError = error instanceof PostFiatError 
        ? error 
        : new PostFiatError(error instanceof Error ? error.message : 'Unknown error');
      setState({ data: null, loading: false, error: postFiatError });
    }
  }, []);

  return [state, execute];
}

/**
 * Hook for wallet operations
 */
export function useWallet() {
  const [walletState, executeWalletOperation] = useAsyncOperation<any>();

  const createWallet = useCallback(async (request: any) => {
    await executeWalletOperation(async () => {
      // TODO: Implement wallet creation when service is generated
      console.log('Creating wallet:', request);
      return { id: 'wallet_' + Date.now(), ...request };
    });
  }, [executeWalletOperation]);

  const getBalance = useCallback(async (walletId: string) => {
    await executeWalletOperation(async () => {
      // TODO: Implement balance retrieval when service is generated
      console.log('Getting balance for wallet:', walletId);
      return { walletId, balance: 100.50, currency: 'USD' };
    });
  }, [executeWalletOperation]);

  return {
    ...walletState,
    createWallet,
    getBalance
  };
}

/**
 * Hook for message operations
 */
export function useMessages() {
  const [messageState, executeMessageOperation] = useAsyncOperation<any>();

  const sendMessage = useCallback(async (message: any) => {
    await executeMessageOperation(async () => {
      // TODO: Implement message sending when service is generated
      console.log('Sending message:', message);
      return { id: 'msg_' + Date.now(), ...message, timestamp: new Date() };
    });
  }, [executeMessageOperation]);

  const getMessages = useCallback(async (conversationId: string) => {
    await executeMessageOperation(async () => {
      // TODO: Implement message retrieval when service is generated
      console.log('Getting messages for conversation:', conversationId);
      return [];
    });
  }, [executeMessageOperation]);

  return {
    ...messageState,
    sendMessage,
    getMessages
  };
}

/**
 * Hook for real-time subscriptions
 */
export function useSubscription<T>(
  subscribe: () => Promise<AsyncIterable<T>>,
  deps: React.DependencyList = []
): AsyncState<T> {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: true,
    error: null
  });

  useEffect(() => {
    let cancelled = false;

    const startSubscription = async () => {
      try {
        const subscription = await subscribe();
        
        if (cancelled) return;
        
        setState({ data: null, loading: false, error: null });
        
        for await (const value of subscription) {
          if (cancelled) break;
          setState({ data: value, loading: false, error: null });
        }
      } catch (error) {
        if (cancelled) return;
        
        const postFiatError = error instanceof PostFiatError 
          ? error 
          : new PostFiatError(error instanceof Error ? error.message : 'Subscription error');
        setState({ data: null, loading: false, error: postFiatError });
      }
    };

    startSubscription();

    return () => {
      cancelled = true;
    };
  }, deps);

  return state;
}
