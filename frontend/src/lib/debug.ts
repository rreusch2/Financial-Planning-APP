import { AxiosError, AxiosResponse } from 'axios';

export const debugLog = {
  request: (url: string, method: string, data?: any) => {
    console.group(`🌐 API Request: ${method.toUpperCase()} ${url}`);
    if (data) console.log('Request Data:', data);
    console.groupEnd();
  },

  response: (response: AxiosResponse) => {
    console.group(`✅ API Response: ${response.status}`);
    console.log('Response Data:', response.data);
    console.log('Headers:', response.headers);
    console.groupEnd();
  },

  error: (error: AxiosError) => {
    console.group('❌ API Error');
    console.log('Status:', error.response?.status);
    console.log('Data:', error.response?.data);
    console.log('Headers:', error.response?.headers);
    console.log('Full Error:', error);
    console.groupEnd();
  }
};