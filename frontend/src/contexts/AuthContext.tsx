import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { User, Session } from '@supabase/supabase-js'
import { supabase } from '../lib/supabase'
import type { User as AppUser } from '../lib/supabase'

// Mock admin user for development
const MOCK_ADMIN_USER: AppUser = {
  id: "8559c7d9-4ce8-4902-8ab9-a52cecd65fc2",
  email: "turhanhamza@gmail.com",
  full_name: "Turhan Hamza",
  company_name: "Agentik Admin",
  phone: "",
  is_admin: true,
  created_at: "2025-08-24T16:17:55.333458",
  updated_at: "2025-08-24T16:17:55.333465"
};

const MOCK_AUTH_USER = {
  id: "c98aa705-729a-475e-bb6b-b16074cb6bac",
  email: "turhanhamza@gmail.com",
  password: "117344", // In real app, this would be hashed
  email_confirmed: true,
  created_at: "2025-08-24T16:17:55.333488",
  user_metadata: {
    full_name: "Turhan Hamza",
    company_name: "Agentik Admin"
  }
};

interface AuthContextType {
  user: User | null
  userProfile: AppUser | null
  session: Session | null
  loading: boolean
  signIn: (email: string, password: string) => Promise<void>
  signUp: (email: string, password: string, metadata?: any) => Promise<void>
  signOut: () => Promise<void>
  updateProfile: (updates: Partial<AppUser>) => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [userProfile, setUserProfile] = useState<AppUser | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check for mock session first
    const mockSession = localStorage.getItem('mock_session');
    const mockUserProfile = localStorage.getItem('mock_user_profile');
    
    if (mockSession && mockUserProfile) {
      try {
        const session = JSON.parse(mockSession) as Session;
        const profile = JSON.parse(mockUserProfile) as AppUser;
        
        // Check if session is still valid (not expired)
        if (session.expires_at && session.expires_at > Date.now()) {
          setSession(session);
          setUser(session.user);
          setUserProfile(profile);
          setLoading(false);
          console.log('🔓 Restored mock admin session for:', profile.email);
          return;
        } else {
          // Clear expired mock session
          localStorage.removeItem('mock_session');
          localStorage.removeItem('mock_user_profile');
        }
      } catch (error) {
        console.error('Error parsing mock session:', error);
        localStorage.removeItem('mock_session');
        localStorage.removeItem('mock_user_profile');
      }
    }
    
    // Get initial Supabase session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setUser(session?.user ?? null)
      if (session?.user) {
        fetchUserProfile(session.user.id)
      } else {
        setLoading(false)
      }
    })

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      setSession(session)
      setUser(session?.user ?? null)
      
      if (session?.user) {
        await fetchUserProfile(session.user.id)
      } else {
        setUserProfile(null)
        setLoading(false)
      }
    })

    return () => subscription.unsubscribe()
  }, [])

  const fetchUserProfile = async (userId: string) => {
    try {
      const { data, error } = await supabase
        .from('users')
        .select('*')
        .eq('id', userId)
        .maybeSingle()

      if (error && error.code !== 'PGRST116') { // PGRST116 is "not found"
        throw error
      }

      if (data) {
        setUserProfile(data as AppUser)
      } else {
        // Create user profile if it doesn't exist
        const newProfile: Partial<AppUser> = {
          id: userId,
          email: user?.email || '',
          full_name: user?.user_metadata?.full_name || '',
          company_name: user?.user_metadata?.company_name || '',
          phone: user?.user_metadata?.phone || '',
          is_admin: false,
        }

        const { data: createdProfile, error: createError } = await supabase
          .from('users')
          .insert([newProfile])
          .select()
          .maybeSingle()

        if (createError) {
          console.error('Error creating user profile:', createError)
        } else if (createdProfile) {
          setUserProfile(createdProfile as AppUser)
        }
      }
    } catch (error) {
      console.error('Error fetching user profile:', error)
    } finally {
      setLoading(false)
    }
  }

  const signIn = async (email: string, password: string) => {
    setLoading(true)
    
    // Check for mock admin authentication first
    if (email === MOCK_AUTH_USER.email && password === MOCK_AUTH_USER.password) {
      // Create mock session for admin user
      const mockUser = {
        id: MOCK_AUTH_USER.id,
        email: MOCK_AUTH_USER.email,
        user_metadata: MOCK_AUTH_USER.user_metadata,
        email_confirmed_at: MOCK_AUTH_USER.created_at,
        created_at: MOCK_AUTH_USER.created_at
      } as User;
      
      const mockSession = {
        user: mockUser,
        access_token: 'mock-admin-token',
        token_type: 'Bearer',
        expires_in: 3600,
        expires_at: Date.now() + 3600000,
        refresh_token: 'mock-refresh-token'
      } as Session;
      
      setUser(mockUser);
      setSession(mockSession);
      setUserProfile(MOCK_ADMIN_USER);
      setLoading(false);
      
      // Store mock session in localStorage
      localStorage.setItem('mock_session', JSON.stringify(mockSession));
      localStorage.setItem('mock_user_profile', JSON.stringify(MOCK_ADMIN_USER));
      
      console.log('🔓 Mock admin login successful:', MOCK_ADMIN_USER.email);
      return;
    }
    
    // Try Supabase authentication
    try {
      const { error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })
      if (error) {
        setLoading(false)
        throw error
      }
    } catch (error) {
      setLoading(false)
      throw error
    }
  }

  const signUp = async (email: string, password: string, metadata: any = {}) => {
    setLoading(true)
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: metadata,
      },
    })
    if (error) {
      setLoading(false)
      throw error
    }
  }

  const signOut = async () => {
    setLoading(true)
    
    // Clear mock session if exists
    const mockSession = localStorage.getItem('mock_session');
    if (mockSession) {
      localStorage.removeItem('mock_session');
      localStorage.removeItem('mock_user_profile');
      setUser(null);
      setSession(null);
      setUserProfile(null);
      setLoading(false);
      console.log('🔓 Mock admin session cleared');
      return;
    }
    
    // Supabase sign out
    const { error } = await supabase.auth.signOut()
    if (error) {
      setLoading(false)
      throw error
    }
  }

  const updateProfile = async (updates: Partial<AppUser>) => {
    if (!user) throw new Error('No user logged in')

    const { data, error } = await supabase
      .from('users')
      .update({ ...updates, updated_at: new Date().toISOString() })
      .eq('id', user.id)
      .select()
      .maybeSingle()

    if (error) throw error
    if (data) {
      setUserProfile(data as AppUser)
    }
  }

  const value: AuthContextType = {
    user,
    userProfile,
    session,
    loading,
    signIn,
    signUp,
    signOut,
    updateProfile,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}