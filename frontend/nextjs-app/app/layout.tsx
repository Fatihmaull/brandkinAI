import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'BrandKin AI - Brand Asset Generation',
  description: 'AI-powered brand identity creation with mascots, avatars, and React components',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}
