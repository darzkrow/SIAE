import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  // Initialize theme from localStorage or default to 'light'
  const [theme, setTheme] = useState(() => {
    const savedTheme = localStorage.getItem('gsih-theme');
    return savedTheme || 'light';
  });

  // Apply theme to document body and save to localStorage
  useEffect(() => {
    // Remove previous theme classes
    document.body.classList.remove('light-mode', 'dark-mode');
    
    // Apply current theme
    if (theme === 'dark') {
      document.body.classList.add('dark-mode');
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.body.classList.add('light-mode');
      document.documentElement.setAttribute('data-theme', 'light');
    }
    
    // Save to localStorage
    localStorage.setItem('gsih-theme', theme);
    
    // Apply AdminLTE theme classes
    const adminLTEClasses = `hold-transition sidebar-mini layout-fixed ${theme === 'dark' ? 'dark-mode' : ''}`;
    document.body.className = adminLTEClasses;
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };

  const setLightTheme = () => setTheme('light');
  const setDarkTheme = () => setTheme('dark');

  const value = {
    theme,
    toggleTheme,
    setLightTheme,
    setDarkTheme,
    isDark: theme === 'dark',
    isLight: theme === 'light'
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export default ThemeContext;