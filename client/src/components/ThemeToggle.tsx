import { createContext, useContext, useEffect, type ReactNode } from 'react'
import type { Theme } from '@/lib/types'

const ThemeContext = createContext<{
  theme: Theme
  setTheme: (t: Theme) => void
}>({ theme: 'light', setTheme: () => {} })

export function useTheme() {
  return useContext(ThemeContext)
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  useEffect(() => {
    const root = document.documentElement
    root.classList.remove('dark')
    root.classList.add('light')
  }, [])

  return (
    <ThemeContext.Provider value={{ theme: 'light', setTheme: () => {} }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function ThemeToggle() {
  return null
}
