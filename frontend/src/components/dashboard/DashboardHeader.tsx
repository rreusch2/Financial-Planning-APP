import React from 'react';
import { Layout, Menu, Button, Avatar } from 'antd';
import { UserOutlined, LogoutOutlined } from '@ant-design/icons';
import type { User } from '../../types/auth';

const { Header } = Layout;

interface DashboardHeaderProps {
  user: User | null;
}

const DashboardHeader: React.FC<DashboardHeaderProps> = ({ user }) => {
  return (
    <Header className="dashboard-header">
      <div className="header-content">
        <div className="logo">
          <h1>Financial Dashboard</h1>
        </div>
        <div className="user-info">
          <Avatar icon={<UserOutlined />} />
          <span className="username">{user?.username}</span>
          <Button 
            type="link" 
            icon={<LogoutOutlined />}
            onClick={() => {/* Add logout handler */}}
          >
            Logout
          </Button>
        </div>
      </div>

      <style jsx>{`
        .dashboard-header {
          background: #fff;
          padding: 0 24px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }

        .header-content {
          display: flex;
          justify-content: space-between;
          align-items: center;
          height: 100%;
        }

        .logo h1 {
          margin: 0;
          color: #1890ff;
          font-size: 1.5rem;
        }

        .user-info {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .username {
          margin: 0 12px;
          color: #666;
        }
      `}</style>
    </Header>
  );
};

export default DashboardHeader; 