import { AgentScopeRuntimeWebUI, IAgentScopeRuntimeWebUIRef, IAgentScopeRuntimeWebUIOptions } from '@agentscope-ai/chat';
import OptionsPanel from './OptionsPanel';
import TaskStatusPanel from './TaskStatusPanel';
import { useMemo, useRef, useEffect } from 'react';
import { Space } from 'antd';
import { parseSSEStream } from '../../utils/sseParser';
import sessionApi from './sessionApi';
import { useLocalStorageState } from 'ahooks';
import defaultConfig from './OptionsPanel/defaultConfig';
import Weather from '../Cards/Weather';
import senderOptions from './Sender';
import { useSimpleStateListener } from './useAgentScopeListener';
import { IAgentScopeRuntimeWebUIMessage } from "@agentscope-ai/chat";

export default function () {
  const chatRef = useRef<IAgentScopeRuntimeWebUIRef>(null);

  // @ts-ignore
  window.chatRef = chatRef;

  useEffect(() => {
    const handleCustomCancel = (event: Event) => {
      const customEvent = event as CustomEvent;
      console.log('🚫 Custom cancel handler:', customEvent.detail);
      senderOptions.onCancel();
    };

    document.addEventListener('handleCustomCancel', handleCustomCancel);

    return () => {
      document.removeEventListener('handleCustomCancel', handleCustomCancel);
    };
  }, []);

  useSimpleStateListener(() => {
    console.log('🎯 AgentScope state listener triggered!');
    senderOptions.onCancel();
  });

  const [optionsConfig, setOptionsConfig] = useLocalStorageState('agent-scope-runtime-webui-options', {
    defaultValue: defaultConfig,
    listenStorageChange: true,
  });

  // 初始化 localStorage：如果缺少配置，立即设置默认值
  useEffect(() => {
    const currentConfigStr = localStorage.getItem('agent-scope-runtime-webui-options');
    if (!currentConfigStr) {
      console.log('⚠️ localStorage 为空，设置默认配置');
      setOptionsConfig(defaultConfig);
    }
  }, []);

  // SSE 任务事件分发监听器
  // 注意：如果 @agentscope-ai/chat 库内部的 SSE 处理支持自定义回调，
  // 可以在这里配置拦截器来分发任务事件到 TaskStatusPanel
  useEffect(() => {
    // 这个 useEffect 作为一个示例，展示如何拦截和处理 SSE 任务事件
    // 实际集成可能需要根据 @agentscope-ai/chat 库的具体实现调整

    const handleSSETaskEvent = (event: CustomEvent) => {
      const detail = event.detail;
      // 确保任务事件被正确分发到 TaskStatusPanel
      console.log('📨 SSE 任务事件拦截:', detail);
    };

    // 监听可能来自库内部的 SSE 事件
    document.addEventListener('sse-task-event', handleSSETaskEvent as EventListener);

    return () => {
      document.removeEventListener('sse-task-event', handleSSETaskEvent as EventListener);
    };
  }, []);

  const options = useMemo(() => {

    const rightHeader = <Space>
      <OptionsPanel value={optionsConfig} onChange={(v: typeof optionsConfig) => {
        setOptionsConfig(prev => ({
          ...prev,
          ...v,
        }));
      }} />
    </Space>;



    const result = {
      ...optionsConfig,
      session: {
        multiple: true,
        api: sessionApi,
      },
      theme: {
        ...optionsConfig.theme,
        rightHeader,
      },
      sender: {
        ...optionsConfig.sender,
        ...senderOptions,
        attachments: optionsConfig.sender.attachments ? senderOptions.attachments : {},

      },
      customToolRenderConfig: {
        'weather search mock': Weather,
      },
    } as unknown as IAgentScopeRuntimeWebUIOptions;


    return result;
  }, [optionsConfig]);

  return (
    <>
      <div style={{ height: '100vh' }}>
        <AgentScopeRuntimeWebUI
          options={options}
        />
      </div>
      <TaskStatusPanel />
    </>
  );
}