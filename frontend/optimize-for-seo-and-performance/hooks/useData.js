import { useState, useEffect } from 'react';

const useData = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    // fetch data
  }, []);

  return data;
};

export default useData;