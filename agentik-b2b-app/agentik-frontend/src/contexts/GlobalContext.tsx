import { createContext, useContext, useReducer, ReactNode } from 'react'

// Types
interface GlobalState {
  notifications: Notification[]
  rfqs: RFQ[]
  suppliers: Supplier[]
  user: UserProfile | null
  loading: {
    rfqs: boolean
    notifications: boolean
    suppliers: boolean
  }
  error: {
    message: string
    details?: any
  } | null
}

interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  read: boolean
  createdAt: string
  metadata?: Record<string, any>
}

interface RFQ {
  id: string
  title: string
  status: 'draft' | 'published' | 'closed' | 'awarded'
  company: string
  deadline: string
  offerCount: number
  createdAt: string
}

interface Supplier {
  id: string
  name: string
  rating: number
  verified: boolean
  categories: string[]
}

interface UserProfile {
  id: string
  email: string
  fullName: string
  companyName: string
  role: string
}

// Actions
type GlobalAction = 
  | { type: 'SET_LOADING'; payload: { key: keyof GlobalState['loading']; value: boolean } }
  | { type: 'SET_ERROR'; payload: { message: string; details?: any } }
  | { type: 'CLEAR_ERROR' }
  | { type: 'ADD_NOTIFICATION'; payload: Notification }
  | { type: 'MARK_NOTIFICATION_READ'; payload: string }
  | { type: 'SET_NOTIFICATIONS'; payload: Notification[] }
  | { type: 'SET_RFQS'; payload: RFQ[] }
  | { type: 'ADD_RFQ'; payload: RFQ }
  | { type: 'UPDATE_RFQ'; payload: { id: string; data: Partial<RFQ> } }
  | { type: 'SET_SUPPLIERS'; payload: Supplier[] }
  | { type: 'SET_USER_PROFILE'; payload: UserProfile | null }

// Initial State
const initialState: GlobalState = {
  notifications: [],
  rfqs: [],
  suppliers: [],
  user: null,
  loading: {
    rfqs: false,
    notifications: false,
    suppliers: false
  },
  error: null
}

// Reducer
function globalReducer(state: GlobalState, action: GlobalAction): GlobalState {
  switch (action.type) {
    case 'SET_LOADING':
      return {
        ...state,
        loading: {
          ...state.loading,
          [action.payload.key]: action.payload.value
        }
      }
    
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload
      }
    
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null
      }
    
    case 'ADD_NOTIFICATION':
      return {
        ...state,
        notifications: [action.payload, ...state.notifications]
      }
    
    case 'MARK_NOTIFICATION_READ':
      return {
        ...state,
        notifications: state.notifications.map(notification =>
          notification.id === action.payload
            ? { ...notification, read: true }
            : notification
        )
      }
    
    case 'SET_NOTIFICATIONS':
      return {
        ...state,
        notifications: action.payload
      }
    
    case 'SET_RFQS':
      return {
        ...state,
        rfqs: action.payload
      }
    
    case 'ADD_RFQ':
      return {
        ...state,
        rfqs: [action.payload, ...state.rfqs]
      }
    
    case 'UPDATE_RFQ':
      return {
        ...state,
        rfqs: state.rfqs.map(rfq =>
          rfq.id === action.payload.id
            ? { ...rfq, ...action.payload.data }
            : rfq
        )
      }
    
    case 'SET_SUPPLIERS':
      return {
        ...state,
        suppliers: action.payload
      }
    
    case 'SET_USER_PROFILE':
      return {
        ...state,
        user: action.payload
      }
    
    default:
      return state
  }
}

// Context
interface GlobalContextType {
  state: GlobalState
  dispatch: React.Dispatch<GlobalAction>
  // Helper functions
  setLoading: (key: keyof GlobalState['loading'], value: boolean) => void
  setError: (message: string, details?: any) => void
  clearError: () => void
  addNotification: (notification: Omit<Notification, 'id' | 'createdAt'>) => void
  markNotificationRead: (id: string) => void
  getUnreadNotificationsCount: () => number
}

const GlobalContext = createContext<GlobalContextType | undefined>(undefined)

// Provider
interface GlobalProviderProps {
  children: ReactNode
}

export function GlobalProvider({ children }: GlobalProviderProps) {
  const [state, dispatch] = useReducer(globalReducer, initialState)

  // Helper functions
  const setLoading = (key: keyof GlobalState['loading'], value: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: { key, value } })
  }

  const setError = (message: string, details?: any) => {
    dispatch({ type: 'SET_ERROR', payload: { message, details } })
  }

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' })
  }

  const addNotification = (notification: Omit<Notification, 'id' | 'createdAt'>) => {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString() + Math.random().toString(36),
      createdAt: new Date().toISOString()
    }
    dispatch({ type: 'ADD_NOTIFICATION', payload: newNotification })
  }

  const markNotificationRead = (id: string) => {
    dispatch({ type: 'MARK_NOTIFICATION_READ', payload: id })
  }

  const getUnreadNotificationsCount = () => {
    return state.notifications.filter(n => !n.read).length
  }

  const contextValue: GlobalContextType = {
    state,
    dispatch,
    setLoading,
    setError,
    clearError,
    addNotification,
    markNotificationRead,
    getUnreadNotificationsCount
  }

  return (
    <GlobalContext.Provider value={contextValue}>
      {children}
    </GlobalContext.Provider>
  )
}

// Hook
export function useGlobalState() {
  const context = useContext(GlobalContext)
  if (context === undefined) {
    throw new Error('useGlobalState must be used within a GlobalProvider')
  }
  return context
}

// Export types
export type { GlobalState, Notification, RFQ, Supplier, UserProfile }
