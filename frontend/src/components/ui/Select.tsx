import React, { createContext, useContext, useState, ReactNode } from 'react'
import { ChevronDown } from 'lucide-react'
import { cn } from '../../lib/utils'

interface SelectContextType {
  value: string
  onValueChange: (value: string) => void
  open: boolean
  setOpen: (open: boolean) => void
}

const SelectContext = createContext<SelectContextType | null>(null)

interface SelectProps {
  children: ReactNode
  value?: string
  defaultValue?: string
  onValueChange?: (value: string) => void
}

export function Select({ children, value, defaultValue, onValueChange }: SelectProps) {
  const [internalValue, setInternalValue] = useState(defaultValue || '')
  const [open, setOpen] = useState(false)

  const currentValue = value !== undefined ? value : internalValue

  const handleValueChange = (newValue: string) => {
    if (value === undefined) {
      setInternalValue(newValue)
    }
    onValueChange?.(newValue)
    setOpen(false)
  }

  return (
    <SelectContext.Provider
      value={{
        value: currentValue,
        onValueChange: handleValueChange,
        open,
        setOpen
      }}
    >
      <div className="relative">{children}</div>
    </SelectContext.Provider>
  )
}

interface SelectTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode
}

export function SelectTrigger({ children, className, ...props }: SelectTriggerProps) {
  const context = useContext(SelectContext)
  if (!context) throw new Error('SelectTrigger must be used within Select')

  const { open, setOpen } = context

  return (
    <button
      type="button"
      className={cn(
        'flex h-9 w-full items-center justify-between whitespace-nowrap rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50',
        className
      )}
      onClick={() => setOpen(!open)}
      {...props}
    >
      {children}
      <ChevronDown className="h-4 w-4 opacity-50" />
    </button>
  )
}

interface SelectValueProps {
  placeholder?: string
}

export function SelectValue({ placeholder }: SelectValueProps) {
  const context = useContext(SelectContext)
  if (!context) throw new Error('SelectValue must be used within Select')

  const { value } = context

  return (
    <span className={cn(value ? 'text-foreground' : 'text-muted-foreground')}>
      {value || placeholder}
    </span>
  )
}

interface SelectContentProps {
  children: ReactNode
  className?: string
}

export function SelectContent({ children, className }: SelectContentProps) {
  const context = useContext(SelectContext)
  if (!context) throw new Error('SelectContent must be used within Select')

  const { open, setOpen } = context

  if (!open) return null

  return (
    <>
      <div
        className="fixed inset-0 z-40"
        onClick={() => setOpen(false)}
      />
      <div
        className={cn(
          'absolute top-full z-50 mt-1 max-h-60 w-full overflow-auto rounded-md border bg-popover text-popover-foreground shadow-md',
          className
        )}
      >
        {children}
      </div>
    </>
  )
}

interface SelectItemProps {
  children: ReactNode
  value: string
  className?: string
}

export function SelectItem({ children, value, className }: SelectItemProps) {
  const context = useContext(SelectContext)
  if (!context) throw new Error('SelectItem must be used within Select')

  const { value: selectedValue, onValueChange } = context

  return (
    <div
      className={cn(
        'relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-2 pr-8 text-sm outline-none hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground',
        selectedValue === value && 'bg-accent',
        className
      )}
      onClick={() => onValueChange(value)}
    >
      {children}
    </div>
  )
}