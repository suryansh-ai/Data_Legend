/**
 * VoiceInput Component — Speech-to-text input with language support.
 * Provides microphone button with visual feedback and transcript display.
 */

import React, { useState, useEffect } from 'react';
import { useVoiceInput, SUPPORTED_LANGUAGES, detectLanguage } from '../hooks/useVoiceInput';

interface VoiceInputProps {
  onTranscript: (text: string) => void;
  placeholder?: string;
  language?: string;
  className?: string;
  disabled?: boolean;
}

export function VoiceInput({
  onTranscript,
  placeholder = "Speak or type your symptoms...",
  language = 'en-IN',
  className = '',
  disabled = false,
}: VoiceInputProps) {
  const [selectedLanguage, setSelectedLanguage] = useState(language);
  const [textInput, setTextInput] = useState('');

  const {
    isListening,
    transcript,
    interimTranscript,
    error,
    isSupported,
    startListening,
    stopListening,
    resetTranscript,
  } = useVoiceInput({
    language: selectedLanguage,
    continuous: false,
    interimResults: true,
    onResult: (text, isFinal) => {
      if (isFinal) {
        onTranscript(text);
      }
    },
    onError: (err) => {
      console.error('Voice input error:', err);
    },
  });

  // Update transcript when voice input completes
  useEffect(() => {
    if (transcript && !isListening) {
      onTranscript(transcript);
    }
  }, [transcript, isListening, onTranscript]);

  // Auto-detect language from text input
  useEffect(() => {
    if (textInput) {
      const detectedLang = detectLanguage(textInput);
      if (detectedLang !== selectedLanguage) {
        setSelectedLanguage(detectedLang);
      }
    }
  }, [textInput, selectedLanguage]);

  const handleTextSubmit = () => {
    if (textInput.trim()) {
      onTranscript(textInput.trim());
      setTextInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleTextSubmit();
    }
  };

  return (
    <div className={`voice-input-container ${className}`}>
      <div className="flex items-center gap-2">
        {/* Voice Input Button */}
        <button
          type="button"
          onClick={isListening ? stopListening : startListening}
          disabled={disabled || !isSupported}
          className={`
            p-3 rounded-full transition-all duration-200
            ${isListening 
              ? 'bg-red-500 text-white animate-pulse' 
              : 'bg-blue-500 text-white hover:bg-blue-600'
            }
            ${disabled || !isSupported ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          `}
          title={isListening ? 'Stop listening' : 'Start voice input'}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            {isListening ? (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            ) : (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
              />
            )}
          </svg>
        </button>

        {/* Text Input */}
        <input
          type="text"
          value={textInput}
          onChange={(e) => setTextInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-600"
        />

        {/* Language Selector */}
        <select
          value={selectedLanguage}
          onChange={(e) => setSelectedLanguage(e.target.value)}
          disabled={disabled || isListening}
          className="p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-600"
        >
          {SUPPORTED_LANGUAGES.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.name}
            </option>
          ))}
        </select>

        {/* Submit Button */}
        <button
          type="button"
          onClick={handleTextSubmit}
          disabled={disabled || !textInput.trim()}
          className="p-3 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
        </button>
      </div>

      {/* Status Display */}
      {(isListening || interimTranscript) && (
        <div className="mt-2 p-3 bg-blue-50 dark:bg-blue-900 rounded-lg">
          <div className="flex items-center gap-2">
            {isListening && (
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-red-600 dark:text-red-400">Listening...</span>
              </div>
            )}
            {interimTranscript && (
              <p className="text-sm text-gray-600 dark:text-gray-300 italic">
                {interimTranscript}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mt-2 p-3 bg-red-50 dark:bg-red-900 rounded-lg">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Not Supported Warning */}
      {!isSupported && (
        <div className="mt-2 p-3 bg-yellow-50 dark:bg-yellow-900 rounded-lg">
          <p className="text-sm text-yellow-600 dark:text-yellow-400">
            Voice input is not supported in your browser. Please use text input.
          </p>
        </div>
      )}
    </div>
  );
}