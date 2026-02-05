import { AgentScopeRuntimeWebUI, IAgentScopeRuntimeWebUIRef, IAgentScopeRuntimeWebUIOptions } from '@agentscope-ai/chat';
import OptionsPanel from './OptionsPanel';
import { useMemo, useRef, useEffect } from 'react';
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

  const options = useMemo(() => {

    const rightHeader = <OptionsPanel value={optionsConfig} onChange={(v: typeof optionsConfig) => {
      setOptionsConfig(prev => ({
        ...prev,
        ...v,
      }));
    }} />;



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

  return <div style={{ height: '100vh' }}>
    <AgentScopeRuntimeWebUI
      options={options}
    />
  </div>;
}