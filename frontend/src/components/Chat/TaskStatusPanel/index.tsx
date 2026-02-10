import { useState, useEffect } from 'react';
import { createStyles } from 'antd-style';
import { Progress, List, Tag, Space, Typography, Empty, Tooltip } from 'antd';
import {
  CheckCircleOutlined,
  SyncOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  DeleteOutlined,
  ClearOutlined,
  RightOutlined,
  LeftOutlined
} from '@ant-design/icons';
import { useLocalStorageState } from 'ahooks';
import type { SSETaskEvent } from '../../../utils/sseParser';

const { Text, Title } = Typography;

interface Task {
  task_id: string;
  task_type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  message?: string;
  error?: string;
  created_at: number;
  updated_at: number;
}

const STATUS_CONFIG = {
  pending: { color: 'default' as const, icon: <ClockCircleOutlined />, text: '等待中' },
  running: { color: 'processing' as const, icon: <SyncOutlined spin />, text: '运行中' },
  completed: { color: 'success' as const, icon: <CheckCircleOutlined />, text: '已完成' },
  failed: { color: 'error' as const, icon: <CloseCircleOutlined />, text: '失败' },
};

const useStyles = createStyles(({ token }) => ({
  panel: {
    width: 380,
    height: '100vh',
    background: token.colorBgContainer,
    borderLeft: `1px solid ${token.colorBorderSecondary}`,
    display: 'flex',
    flexDirection: 'column',
    position: 'fixed',
    right: 0,
    top: 0,
    zIndex: 1000,
    transition: 'transform 0.3s ease',
  },
  panelCollapsed: {
    transform: 'translateX(100%)',
  },
  toggleBtn: {
    position: 'absolute',
    left: -32,
    top: '50%',
    transform: 'translateY(-50%)',
    width: 32,
    height: 64,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: token.colorBgContainer,
    border: `1px solid ${token.colorBorderSecondary}`,
    borderRight: 'none',
    borderRadius: '8px 0 0 8px',
    cursor: 'pointer',
    fontSize: 16,
    color: token.colorTextSecondary,
    '&:hover': {
      color: token.colorPrimary,
      background: token.colorBgLayout,
    },
  },
  container: { height: '100%', display: 'flex', flexDirection: 'column' },
  content: { height: 0, flex: 1, padding: '16px', overflow: 'auto' },
  header: { padding: '16px', borderBottom: `1px solid ${token.colorBorderSecondary}` },
  taskItem: {
    marginBottom: 12,
    padding: 12,
    borderRadius: 8,
    background: token.colorBgContainer,
    border: `1px solid ${token.colorBorderSecondary}`,
    transition: 'all 0.2s',
    '&:hover': { borderColor: token.colorPrimary, boxShadow: token.boxShadow },
  },
  taskHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  stats: { display: 'flex', gap: 12, fontSize: 12 },
}));

export default function TaskStatusPanel() {
  const [collapsed, setCollapsed] = useState(false);
  const { styles, cx } = useStyles();
  const [tasks, setTasks] = useLocalStorageState<Task[]>('scrapy-tasks', {
    defaultValue: [],
    listenStorageChange: true,
  });

  const runningCount = tasks.filter(t => t.status === 'running').length;
  const completedCount = tasks.filter(t => t.status === 'completed').length;
  const failedCount = tasks.filter(t => t.status === 'failed').length;

  useEffect(() => {
    const handleTaskEvent = (event: Event) => {
      const customEvent = event as CustomEvent<SSETaskEvent>;
      const detail = customEvent.detail;

      console.log('📥 收到任务事件:', detail);

      setTasks((prevTasks = []) => {
        const existingIndex = prevTasks.findIndex(t => t.task_id === detail.task_id);

        if (existingIndex >= 0) {
          const updated = [...prevTasks];
          updated[existingIndex] = {
            ...updated[existingIndex],
            status: detail.status,
            progress: detail.progress,
            message: detail.message,
            error: detail.error,
            updated_at: Date.now() / 1000,
          };
          return updated;
        } else {
          const newTask: Task = {
            task_id: detail.task_id,
            task_type: detail.task_type,
            status: detail.status,
            progress: detail.progress,
            message: detail.message,
            error: detail.error,
            created_at: detail.timestamp || Date.now() / 1000,
            updated_at: detail.timestamp || Date.now() / 1000,
          };
          return [newTask, ...prevTasks];
        }
      });
    };

    document.addEventListener('sse-task-event', handleTaskEvent);
    return () => document.removeEventListener('sse-task-event', handleTaskEvent);
  }, [setTasks]);

  const handleDeleteTask = (taskId: string) => {
    setTasks((prev = []) => prev.filter(t => t.task_id !== taskId));
  };

  const handleClearCompleted = () => {
    setTasks((prev = []) => prev.filter(t => t.status !== 'completed' && t.status !== 'failed'));
  };

  const handleClearAll = () => {
    setTasks([]);
  };

  return (
    <div className={cx(styles.panel, collapsed && styles.panelCollapsed)}>
      <div className={styles.toggleBtn} onClick={() => setCollapsed(!collapsed)}>
        {collapsed ? <LeftOutlined /> : <RightOutlined />}
      </div>

      {!collapsed && (
        <>
          <div className={styles.header}>
            <Space direction="vertical" size={4} style={{ width: '100%' }}>
              <Space style={{ justifyContent: 'space-between', width: '100%' }}>
                <Title level={5} style={{ margin: 0 }}>任务状态</Title>
                <Space>
                  {tasks.length > 0 && (
                    <>
                      <Tooltip title="清空已完成">
                        <div
                          onClick={handleClearCompleted}
                          style={{ cursor: 'pointer', fontSize: 14, color: '#8c8c8c' }}
                        >
                          <ClearOutlined />
                        </div>
                      </Tooltip>
                      <Tooltip title="清空所有">
                        <div
                          onClick={handleClearAll}
                          style={{ cursor: 'pointer', fontSize: 14, color: '#8c8c8c' }}
                        >
                          <DeleteOutlined />
                        </div>
                      </Tooltip>
                    </>
                  )}
                </Space>
              </Space>
              {tasks.length > 0 && (
                <div className={styles.stats}>
                  <Text type="secondary">总计: {tasks.length}</Text>
                  <Text type="success">已完成: {completedCount}</Text>
                  <Text type="warning">运行中: {runningCount}</Text>
                  {failedCount > 0 && <Text type="danger">失败: {failedCount}</Text>}
                </div>
              )}
            </Space>
          </div>

          <div className={styles.content}>
            {tasks.length === 0 ? (
              <Empty description="暂无任务" image={Empty.PRESENTED_IMAGE_SIMPLE} />
            ) : (
              <List
                dataSource={tasks}
                renderItem={(task) => {
                  const config = STATUS_CONFIG[task.status];
                  return (
                    <div key={task.task_id} className={styles.taskItem}>
                      <Space direction="vertical" size={4} style={{ width: '100%' }}>
                        <div className={styles.taskHeader}>
                          <Space>
                            <Text strong>{task.task_type}</Text>
                            <Tag color={config.color} icon={config.icon}>{config.text}</Tag>
                          </Space>
                          <Tooltip title="删除此任务">
                            <div
                              onClick={() => handleDeleteTask(task.task_id)}
                              style={{ cursor: 'pointer', fontSize: 12, color: '#8c8c8c' }}
                            >
                              <DeleteOutlined />
                            </div>
                          </Tooltip>
                        </div>
                        {task.status === 'running' && (
                          <Progress
                            percent={task.progress}
                            size="small"
                            status="active"
                            strokeColor={{ '0%': '#108ee9', '100%': '#87d068' }}
                          />
                        )}
                        {task.progress > 0 && task.progress < 100 && (
                          <Text type="secondary" style={{ fontSize: 11 }}>进度: {task.progress}%</Text>
                        )}
                        {task.message && <Text type="secondary" style={{ fontSize: 12 }}>{task.message}</Text>}
                        {task.status === 'failed' && task.error && (
                          <Text type="danger" style={{ fontSize: 12 }}>❌ {task.error}</Text>
                        )}
                        <Text type="secondary" style={{ fontSize: 11 }}>
                          {new Date(task.created_at * 1000).toLocaleString('zh-CN', {
                            month: '2-digit',
                            day: '2-digit',
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit'
                          })}
                        </Text>
                      </Space>
                    </div>
                  );
                }}
              />
            )}
          </div>
        </>
      )}
    </div>
  );
}
