import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import EstablishDeploymentAndMaintenancePlan from '../components/index';

describe('EstablishDeploymentAndMaintenancePlan', () => {
  it('renders correctly', () => {
    const { container } = render(<EstablishDeploymentAndMaintenancePlan />);
    expect(container).toMatchSnapshot();
  });
});