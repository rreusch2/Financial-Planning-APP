// src/api.js
export async function fetchAccountSummary() {
    try {
      const response = await fetch('/api/account_summary');
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch account summary');
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching account summary:', error);
      throw error;
    }
  }
  
  export async function fetchTransactions(startDate, endDate) {
    try {
      const url = startDate && endDate 
        ? `/api/transactions?start_date=${startDate}&end_date=${endDate}`
        : '/api/transactions';
        
      const response = await fetch(url);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch transactions');
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching transactions:', error);
      throw error;
    }
  }
  
  export async function fetchBudgets() {
    try {
      const response = await fetch('/api/budgets');
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch budgets');
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching budgets:', error);
      throw error;
    }
  }
  
  export async function addIncome(incomeData) {
    try {
      const response = await fetch('/api/income', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(incomeData),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to add income');
      }
      return await response.json();
    } catch (error) {
      console.error('Error adding income:', error);
      throw error;
    }
  }
  
  export async function fetchAIAdvice() {
    try {
      const response = await fetch('/api/ai_advice');
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch AI advice');
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching AI advice:', error);
      throw error;
    }
  }
  
  // Helper function to handle common fetch operations
  async function fetchWithError(url, options = {}) {
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
  
      return await response.json();
    } catch (error) {
      console.error(`Error fetching ${url}:`, error);
      throw error;
    }
  }
  
  module.exports = {
    fetchAccountSummary,
    fetchTransactions,
    fetchBudgets,
    addIncome,
    fetchAIAdvice
  };