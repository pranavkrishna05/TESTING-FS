import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import ImplementAnalyticsAndReporting from '../components/index';

describe('ImplementAnalyticsAndReporting', () => {
  it('renders correctly', () => {
    const { container } = render(<ImplementAnalyticsAndReporting />);
    expect(container).toMatchSnapshot();
  });
});