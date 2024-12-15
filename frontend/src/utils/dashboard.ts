export const getHealthScoreStatus = (score: number) => {
  if (score >= 80) return 'success';
  if (score >= 60) return 'normal';
  return 'exception';
}; 