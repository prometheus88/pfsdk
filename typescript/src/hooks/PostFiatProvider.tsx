import React, { createContext, useContext, ReactNode } from 'react';
import { PostFiatClient } from '../sdk/client';
import type { ClientOptions } from '../sdk/config';

/**
 * Context for PostFiat SDK
 */
export interface PostFiatContextValue {
  client: PostFiatClient;
  config: ClientOptions;
}

export const PostFiatContext = createContext<PostFiatContextValue | null>(null);

/**
 * Props for PostFiatProvider
 */
export interface PostFiatProviderProps {
  children: ReactNode;
  config: ClientOptions;
}

/**
 * Provider component for PostFiat SDK
 */
export function PostFiatProvider({ children, config }: PostFiatProviderProps) {
  const client = new PostFiatClient(config);
  
  const value: PostFiatContextValue = {
    client,
    config,
  };

  return (
    <PostFiatContext.Provider value={value}>
      {children}
    </PostFiatContext.Provider>
  );
}

/**
 * Hook to use PostFiat context
 */
export function usePostFiat() {
  const context = useContext(PostFiatContext);
  
  if (!context) {
    throw new Error('usePostFiat must be used within a PostFiatProvider');
  }
  
  return context;
}