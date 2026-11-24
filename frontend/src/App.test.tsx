import '@testing-library/jest-dom/vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import App from './App'

describe('WebPilot AI', () => {
  it('renders the landing page', () => {
    render(<MemoryRouter><App /></MemoryRouter>)
    expect(screen.getByText(/Turn complex web processes/i)).toBeInTheDocument()
  })
})
