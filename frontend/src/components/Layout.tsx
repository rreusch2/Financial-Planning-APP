import React from 'react';
import { Layout as AntLayout } from 'antd';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

const { Content } = AntLayout;

const Layout: React.FC = () => {
  return (
    <AntLayout className="min-h-screen">
      <Sidebar />
      <AntLayout>
        <Content className="p-6">
          <Outlet />
        </Content>
      </AntLayout>
    </AntLayout>
  );
};

export default Layout;