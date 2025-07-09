import { useContext } from 'react';
import { PostFiatContext } from './PostFiatProvider';

/**
 * Hook to use PostFiat client from context
 */
export function usePostFiatClient() {
  const context = useContext(PostFiatContext);
  
  if (!context) {
    throw new Error('usePostFiatClient must be used within a PostFiatProvider');
  }
  
  return context;
}