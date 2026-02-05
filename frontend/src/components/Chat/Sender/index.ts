import { IAgentScopeRuntimeWebUISenderAttachmentsOptions, IAgentScopeRuntimeWebUISenderOptions } from "@agentscope-ai/chat";
import attachmentOptions from "./attachment";

class SenderOptions implements IAgentScopeRuntimeWebUISenderOptions {
    lsKey: string;
    abortController: AbortController | null = null;

    constructor() {
        this.lsKey = 'agent-scope-runtime-webui-options';
    }


    async beforeSubmit() {
        console.log('🚀 Before submitting query:');
        return true;
    }

    async onSubmit(data: { query: string; fileList?: any[]; }) {
        console.log('🚀 Submitting query:', data);
    }

    async onCancel() {
        console.log('🚫 Cancelling current request...');

        if (this.abortController) {
            this.abortController.abort();
            this.abortController = null;
        }
    }

    attachments: IAgentScopeRuntimeWebUISenderAttachmentsOptions = attachmentOptions;
}

export default new SenderOptions();

