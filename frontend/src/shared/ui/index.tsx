// Small, generic UI primitives. They know nothing about sentiment analysis.
import type { ButtonHTMLAttributes, CSSProperties, ReactNode } from 'react'
import styles from './ui.module.css'

import { cx } from './cx'

interface CardProps {
  title?: ReactNode
  actions?: ReactNode
  children: ReactNode
  className?: string
}

export function Card({ title, actions, children, className }: CardProps) {
  return (
    <section className={cx(styles.card, className)}>
      {(title || actions) && (
        <header className={styles.cardHeader}>
          {title && <h2 className={styles.cardTitle}>{title}</h2>}
          {actions}
        </header>
      )}
      <div className={styles.cardBody}>{children}</div>
    </section>
  )
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'md' | 'sm'
  loading?: boolean
}

export function Button({
  variant = 'secondary',
  size = 'md',
  loading = false,
  className,
  children,
  disabled,
  ...rest
}: ButtonProps) {
  return (
    <button
      type="button"
      className={cx(styles.button, styles[variant], size === 'sm' && styles.small, className)}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      {...rest}
    >
      {loading && <span className={styles.spinner} aria-hidden />}
      {children}
    </button>
  )
}

interface SwitchProps {
  checked: boolean
  onChange: (checked: boolean) => void
  label: ReactNode
  title?: string
}

export function Switch({ checked, onChange, label, title }: SwitchProps) {
  return (
    <label className={styles.switch} title={title}>
      <input
        type="checkbox"
        role="switch"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
      />
      {label}
    </label>
  )
}

export const Kbd = ({ children }: { children: ReactNode }) => (
  <kbd className={styles.kbd}>{children}</kbd>
)

export function EmptyState({ title, children }: { title: ReactNode; children?: ReactNode }) {
  return (
    <div className={styles.empty}>
      <p className={styles.emptyTitle}>{title}</p>
      {children && <p>{children}</p>}
    </div>
  )
}

export function Alert({ title, children }: { title: ReactNode; children?: ReactNode }) {
  return (
    <div className={styles.alert} role="alert">
      <span className={styles.alertIcon} aria-hidden>
        !
      </span>
      <div>
        <p className={styles.alertTitle}>{title}</p>
        {children && <p>{children}</p>}
      </div>
    </div>
  )
}

export function Skeleton({ width = '100%', height = 14 }: { width?: CSSProperties['width']; height?: number }) {
  return <div className={styles.skeleton} style={{ width, height }} aria-hidden />
}

