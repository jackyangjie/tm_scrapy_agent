import { AgentScopeRuntimeWebUI, IAgentScopeRuntimeWebUIRef, IAgentScopeRuntimeWebUIOptions } from '@agentscope-ai/chat';
import OptionsPanel from './OptionsPanel';
import { useMemo, useRef } from 'react';
import sessionApi from './sessionApi';
import { useLocalStorageState } from 'ahooks';
import defaultConfig from './OptionsPanel/defaultConfig';
import Weather from '../Cards/Weather';

export default function () {
  const chatRef = useRef<IAgentScopeRuntimeWebUIRef>(null);
  // @ts-ignore
  window.chatRef = chatRef;

  const [optionsConfig, setOptionsConfig] = useLocalStorageState('agent-scope-runtime-webui-options', {
    defaultValue: defaultConfig,
    listenStorageChange: true,
  });

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
        attachments: optionsConfig.sender?.attachments ? {
          customRequest(options) {
            // 模拟上传进度
            options.onProgress({
              percent: 100,
            });
            // 当前是一个 mock 的上传行为
            // 实际情况需要具体实现一个文件上传服务，将文件转化为 url
            options.onSuccess({
              url: URL.createObjectURL(options.file as Blob)
            });
          }
        } : undefined,
      },
      customToolRenderConfig: {
        'weather search mock': Weather,
      },
    } as unknown as IAgentScopeRuntimeWebUIOptions;

    console.log('=== Debug Info ===');
    console.log('optionsConfig:', JSON.stringify(optionsConfig, null, 2));
    console.log('optionsConfig.sender:', optionsConfig.sender);
    console.log('optionsConfig.sender.attachments:', optionsConfig.sender?.attachments);
    console.log('Final sender.attachments:', result.sender?.attachments);
    console.log('====================');

    return result;
  }, [optionsConfig]);

  return <div style={{ height: '100vh' }}>
    <AgentScopeRuntimeWebUI
      options={options}
    />
  </div>;
}
