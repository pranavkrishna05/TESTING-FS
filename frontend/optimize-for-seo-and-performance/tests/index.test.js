import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import OptimizeForSeoAndPerformance from '../components/index';

describe('OptimizeForSeoAndPerformance', () => {
  it('renders correctly', () => {
    const { container } = render(<OptimizeForSeoAndPerformance />);
    expect(container).toMatchSnapshot();
  });
});