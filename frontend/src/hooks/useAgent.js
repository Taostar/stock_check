/**
 * React Query hooks for agent data
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { agentApi, holdingsApi, schedulerApi } from '../services/api';

/**
 * Hook to fetch and manage portfolio analysis
 */
export function useAnalysis() {
  const queryClient = useQueryClient();

  const statusQuery = useQuery({
    queryKey: ['agent', 'status'],
    queryFn: agentApi.getStatus,
    refetchInterval: 5000, // Poll every 5 seconds
  });

  const analyzeMutation = useMutation({
    mutationFn: agentApi.analyze,
    onSuccess: () => {
      // Invalidate all agent queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['agent'] });
      queryClient.invalidateQueries({ queryKey: ['holdings'] });
    },
  });

  return {
    status: statusQuery.data,
    isLoading: statusQuery.isLoading,
    analyze: analyzeMutation.mutate,
    isAnalyzing: analyzeMutation.isPending || statusQuery.data?.in_progress,
    error: analyzeMutation.error,
  };
}

/**
 * Hook to fetch AI summary
 */
export function useSummary() {
  return useQuery({
    queryKey: ['agent', 'summary'],
    queryFn: agentApi.getSummary,
    staleTime: 30000, // Consider fresh for 30 seconds
  });
}

/**
 * Hook to fetch fluctuation alerts
 */
export function useFluctuations() {
  return useQuery({
    queryKey: ['agent', 'fluctuations'],
    queryFn: agentApi.getFluctuations,
    staleTime: 30000,
  });
}

/**
 * Hook to fetch upcoming earnings
 */
export function useEarnings() {
  return useQuery({
    queryKey: ['agent', 'earnings'],
    queryFn: agentApi.getEarnings,
    staleTime: 60000, // Earnings don't change often
  });
}

/**
 * Hook to fetch news
 */
export function useNews() {
  return useQuery({
    queryKey: ['agent', 'news'],
    queryFn: agentApi.getNews,
    staleTime: 30000,
  });
}

/**
 * Hook to fetch holdings with performance
 */
export function useHoldingsPerformance(useMock = false) {
  return useQuery({
    queryKey: ['holdings', 'performance', useMock],
    queryFn: () => holdingsApi.getPerformance(useMock),
    staleTime: 30000,
  });
}

/**
 * Hook to manage scheduler
 */
export function useScheduler() {
  const queryClient = useQueryClient();

  const statusQuery = useQuery({
    queryKey: ['scheduler', 'status'],
    queryFn: schedulerApi.getStatus,
    refetchInterval: 10000, // Poll every 10 seconds
  });

  const startMutation = useMutation({
    mutationFn: schedulerApi.start,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scheduler'] });
    },
  });

  const stopMutation = useMutation({
    mutationFn: schedulerApi.stop,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scheduler'] });
    },
  });

  const triggerMutation = useMutation({
    mutationFn: schedulerApi.trigger,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent'] });
      queryClient.invalidateQueries({ queryKey: ['scheduler'] });
    },
  });

  return {
    status: statusQuery.data,
    isLoading: statusQuery.isLoading,
    start: startMutation.mutate,
    stop: stopMutation.mutate,
    trigger: triggerMutation.mutate,
    isTriggering: triggerMutation.isPending,
  };
}
