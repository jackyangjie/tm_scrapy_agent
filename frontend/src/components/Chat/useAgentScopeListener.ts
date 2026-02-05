/**
 * 通过监听 AgentScope 组件内部状态实现取消监听
 */

import { useEffect, useRef, useCallback } from 'react';

/**
 * 最佳方案：通过监听组件内部状态变化
 *
 * 原理：
 * 1. AgentScopeRuntimeWebUI 内部使用 ChatAnywhereInputContext 管理 loading 状态
 * 2. loading 状态变化会触发 UI 更新
 * 3. 通过观察 UI 变化，可以间接监听到状态变化
 */
export function useAgentScopeStateListener(onCancel: () => void) {
  const stateRef = useRef({
    hasLoadingSpinner: false,
    sendButtonDisabled: false,
    stopButtonVisible: false,
    inputReadOnly: false,
    lastMessageTime: 0
  });

  useEffect(() => {
    const checkState = () => {
      // 1. 检查是否有 loading spinner
      const loadingSpinner = document.querySelector('[class*="spin"]');

      // 2. 检查发送按钮是否被禁用
      const sendButton = document.querySelector('button[class*="send"]');
      const sendButtonDisabled = sendButton?.getAttribute('disabled') === 'true';

      // 3. 检查是否有停止按钮
      const stopButton = document.querySelector('[title*="Stop"], [aria-label*="stop"], [class*="stop"]');

      // 4. 检查输入框是否只读
      const textarea = document.querySelector('textarea[disabled], textarea[readonly]');

      // 判断是否正在加载
      const isLoading = !!loadingSpinner ||
                       sendButtonDisabled ||
                       !!stopButton ||
                       !!textarea;

      const wasLoading = stateRef.current.hasLoadingSpinner ||
                         stateRef.current.sendButtonDisabled ||
                         stateRef.current.stopButtonVisible ||
                         !!stateRef.current.inputReadOnly;

      // 从加载状态变为非加载状态 = 取消
      if (wasLoading && !isLoading) {
        console.log('🚫 Cancel detected via AgentScope state!');

        // 添加延迟，确保库内部状态已更新
        setTimeout(() => {
          onCancel();
        }, 50);
      }

      // 更新状态
      stateRef.current = {
        hasLoadingSpinner: !!loadingSpinner,
        sendButtonDisabled: !!sendButtonDisabled,
        stopButtonVisible: !!stopButton,
        inputReadOnly: !!textarea,
        lastMessageTime: Date.now()
      };
    };

    // 使用 MutationObserver 监听 DOM 变化
    const observer = new MutationObserver(() => {
      checkState();
    });

    // 监听整个聊天容器
    const chatContainer = document.querySelector('[class*="chat"]');
    if (chatContainer) {
      observer.observe(chatContainer, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['disabled', 'readonly', 'class', 'aria-label']
      });
    }

    // 同时也使用定时检查作为备选
    const interval = setInterval(checkState, 200);

    return () => {
      observer.disconnect();
      clearInterval(interval);
    };
  }, [onCancel]);
}

/**
 * 简化版：只监听关键元素
 */
export function useSimpleStateListener(onCancel: () => void) {
  const wasLoadingRef = useRef(false);

  useEffect(() => {
    const checkLoading = () => {
      // 核心指标：检查停止按钮和发送按钮
      const stopButton = document.querySelector('[class*="stop"], [title*="Stop"]');
      const sendButton = document.querySelector('button[class*="send"]');
      const isSendDisabled = sendButton?.getAttribute('disabled') === 'true';

      const isLoading = !!stopButton || isSendDisabled;

      if (wasLoadingRef.current && !isLoading) {
        console.log('🚫 Cancel detected (simple)!');
        onCancel();
      }

      wasLoadingRef.current = isLoading;
    };

    // 只监听按钮区域，性能更好
    const observer = new MutationObserver(checkLoading);

    const buttonContainer = document.querySelector('[class*="sender"]') ||
                           document.querySelector('[class*="input"]');

    if (buttonContainer) {
      observer.observe(buttonContainer, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['disabled', 'class']
      });
    }

    return () => observer.disconnect();
  }, [onCancel]);
}

/**
 * 高级版：结合键盘事件
 */
export function useAdvancedStateListener(onCancel: () => void) {
  const wasLoadingRef = useRef(false);

  const handleCancel = useCallback(() => {
    if (wasLoadingRef.current) {
      console.log('🚫 Cancel detected (advanced)!');
      onCancel();
      wasLoadingRef.current = false;
    }
  }, [onCancel]);

  useEffect(() => {
    const checkLoading = () => {
      const stopButton = document.querySelector('[class*="stop"]');
      const sendButton = document.querySelector('button[class*="send"]');
      const isSendDisabled = sendButton?.getAttribute('disabled') === 'true';
      const isLoading = !!stopButton || isSendDisabled;

      wasLoadingRef.current = isLoading;
    };

    // 1. 监听 DOM 变化
    const observer = new MutationObserver(checkLoading);
    const inputArea = document.querySelector('[class*="sender"]');

    if (inputArea) {
      observer.observe(inputArea, {
        childList: true,
        attributes: true,
        subtree: true
      });
    }

    // 2. 监听键盘事件（ESC 键）
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && wasLoadingRef.current) {
        handleCancel();
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    // 3. 定期检查状态
    const interval = setInterval(() => {
      checkLoading();
      if (wasLoadingRef.current && !document.querySelector('[class*="stop"]')) {
        handleCancel();
      }
    }, 300);

    return () => {
      observer.disconnect();
      document.removeEventListener('keydown', handleKeyDown);
      clearInterval(interval);
    };
  }, [handleCancel, onCancel]);
}

/**
 * 使用示例
 */
/*
function ChatComponent() {
  const handleCancel = useCallback(() => {
    console.log('Cancel triggered!');
    senderOptions.onCancel();
  }, []);

  // 方案 1：完整监听（推荐）
  useAgentScopeStateListener(handleCancel);

  // 方案 2：简化监听
  useSimpleStateListener(handleCancel);

  // 方案 3：高级监听（含键盘）
  useAdvancedStateListener(handleCancel);

  return <AgentScopeRuntimeWebUI options={options} />;
}
*/
