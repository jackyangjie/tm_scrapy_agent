"""Bounded memory with token limit management."""

import logging
from typing import Union, Iterable, Any
from agentscope.memory import MemoryBase
from agentscope.message import Msg


class BoundedMemory(MemoryBase):
    """Memory with token limit enforcement.

    Keeps only the most recent messages within token budget.
    Uses sliding window to maintain conversation context.
    """

    def __init__(
        self,
        max_tokens: int = 100000,
        reserve_ratio: float = 0.7,
        max_single_message_tokens: int = 50000,
    ):
        """Initialize bounded memory.

        Args:
            max_tokens: Maximum tokens to store (default 100K)
            reserve_ratio: Reserve this ratio for response (default 0.7)
                          Actual limit = max_tokens * reserve_ratio
            max_single_message_tokens: Maximum tokens for a single message (default 50K)
        """
        super().__init__()
        self.max_tokens = max_tokens
        self.reserve_ratio = reserve_ratio
        self.effective_limit = int(max_tokens * reserve_ratio)
        self.max_single_message_tokens = max_single_message_tokens
        self.content: list[Msg] = []
        self._estimated_tokens = 0

    def state_dict(self) -> dict:
        """Convert memory to state dict."""
        return {
            "content": [_.to_dict() for _ in self.content],
            "max_tokens": self.max_tokens,
            "reserve_ratio": self.reserve_ratio,
        }

    def load_state_dict(
        self,
        state_dict: dict,
        strict: bool = True,
    ) -> None:
        """Load memory from state dict with truncation."""
        self.max_tokens = state_dict.get("max_tokens", self.max_tokens)
        self.reserve_ratio = state_dict.get("reserve_ratio", self.reserve_ratio)
        self.effective_limit = int(self.max_tokens * self.reserve_ratio)

        self.content = []
        for data in state_dict.get("content", []):
            data.pop("type", None)
            msg = Msg.from_dict(data)
            self._add_message_safely(msg)

        self._enforce_token_limit()
        logging.info(
            f"Loaded {len(self.content)} messages "
            f"(~{self._estimated_tokens} tokens, "
            f"limit: {self.effective_limit})"
        )

    def _estimate_tokens(self, msg: Msg) -> int:
        """More accurate token estimation for a message.

        Uses different strategies based on content type:
        - Text content: 1 token ≈ 3 characters (conservative)
        - HTML/code: 1 token ≈ 4 characters (more dense)
        - Binary/base64: 1 token ≈ 5 characters
        """
        text = str(msg.content)

        if text.startswith("<!DOCTYPE html>") or text.startswith("<html"):
            return len(text) // 4
        elif text.startswith("data:") or len(text) // len(text.strip()) > 10:
            return len(text) // 5
        else:
            return len(text) // 3

    def _add_message_safely(self, msg: Msg) -> None:
        """Add message without enforcing limit."""
        self.content.append(msg)
        self._estimated_tokens += self._estimate_tokens(msg)

    def _truncate_message_content(self, msg: Msg, max_tokens: int) -> Msg:
        """Truncate a single message's content if it exceeds token limit."""
        current_tokens = self._estimate_tokens(msg)

        if current_tokens <= max_tokens:
            return msg

        truncate_ratio = max_tokens / current_tokens
        keep_length = int(len(str(msg.content)) * truncate_ratio)

        if isinstance(msg.content, str):
            new_content = (
                msg.content[:keep_length]
                + "\n\n[... Content truncated due to size ...]"
            )
        elif isinstance(msg.content, list):
            new_content = (
                str(msg.content)[:keep_length] + "\n\n[... Content truncated ...]"
            )
        else:
            new_content = (
                str(msg.content)[:keep_length] + "\n\n[... Content truncated ...]"
            )

        from agentscope.message import Msg

        truncated_msg = Msg(
            role=msg.role,
            content=new_content,
            name=getattr(msg, "name", None),
            url=getattr(msg, "url", None),
        )

        logging.warning(
            f"Truncated message from {current_tokens} to {max_tokens} tokens "
            f"(removed {current_tokens - max_tokens} tokens)"
        )

        return truncated_msg

    def _enforce_token_limit(self) -> None:
        """Remove oldest messages and truncate large messages until within token limit."""
        for i in range(len(self.content)):
            msg_tokens = self._estimate_tokens(self.content[i])
            if msg_tokens > self.max_single_message_tokens:
                self.content[i] = self._truncate_message_content(
                    self.content[i], self.max_single_message_tokens
                )
                self._estimated_tokens -= msg_tokens
                self._estimated_tokens += self._estimate_tokens(self.content[i])

        while self._estimated_tokens > self.effective_limit and len(self.content) > 0:
            removed = self.content.pop(0)
            self._estimated_tokens -= self._estimate_tokens(removed)

        if len(self.content) > 0:
            logging.info(
                f"Memory: {len(self.content)} messages, ~{self._estimated_tokens} tokens "
                f"(limit: {self.effective_limit})"
            )
        elif isinstance(msg.content, list):
            new_content = (
                str(msg.content)[:keep_length] + "\n\n[... Content truncated ...]"
            )
        else:
            new_content = (
                str(msg.content)[:keep_length] + "\n\n[... Content truncated ...]"
            )

        # Create new message with truncated content
        from agentscope.message import Msg

        truncated_msg = Msg(
            role=msg.role,
            content=new_content,
            name=getattr(msg, "name", None),
            url=getattr(msg, "url", None),
        )

        logging.warning(
            f"Truncated message from {current_tokens} to {max_tokens} tokens "
            f"(removed {current_tokens - max_tokens} tokens)"
        )

        return truncated_msg

    def _enforce_token_limit(self) -> None:
        """Remove oldest messages and truncate large messages until within token limit."""
        # Step 1: Truncate any single message that exceeds max_single_message_tokens
        for i in range(len(self.content)):
            msg_tokens = self._estimate_tokens(self.content[i])
            if msg_tokens > self.max_single_message_tokens:
                old_msg = self.content[i]
                self.content[i] = self._truncate_message_content(
                    self.content[i], self.max_single_message_tokens
                )
                # Update estimated tokens
                self._estimated_tokens -= msg_tokens
                self._estimated_tokens += self._estimate_tokens(self.content[i])

        # Step 2: Remove oldest messages until within effective limit
        while self._estimated_tokens > self.effective_limit and len(self.content) > 0:
            removed = self.content.pop(0)
            self._estimated_tokens -= self._estimate_tokens(removed)

        if len(self.content) > 0:
            logging.info(
                f"Memory: {len(self.content)} messages, ~{self._estimated_tokens} tokens "
                f"(limit: {self.effective_limit})"
            )

    async def add(
        self,
        memories: Union[list[Msg], Msg, None],
        allow_duplicates: bool = False,
    ) -> None:
        """Add message with automatic token limit enforcement."""
        if memories is None:
            return

        if isinstance(memories, Msg):
            memories = [memories]

        if not isinstance(memories, list):
            raise TypeError(f"Expected list[Msg] or Msg, got {type(memories)}")

        for msg in memories:
            if not isinstance(msg, Msg):
                raise TypeError(f"Expected Msg, got {type(msg)}")

        if not allow_duplicates:
            existing_ids = [_.id for _ in self.content]
            memories = [_ for _ in memories if _.id not in existing_ids]

        for msg in memories:
            self._add_message_safely(msg)

        self._enforce_token_limit()

    async def size(self) -> int:
        """Return number of messages in memory."""
        return len(self.content)

    async def get_memory(self) -> list[Msg]:
        """Get memory content."""
        return self.content

    async def clear(self) -> None:
        """Clear memory."""
        self.content = []
        self._estimated_tokens = 0

    async def delete(self, index: Union[Iterable, int]) -> None:
        """Delete messages by index."""
        if isinstance(index, int):
            index = [index]

        invalid_index = [_ for _ in index if 0 > _ or _ >= len(self.content)]
        if invalid_index:
            raise IndexError(f"Invalid index: {invalid_index}")

        for idx in sorted(index, reverse=True):
            removed = self.content.pop(idx)
            self._estimated_tokens -= self._estimate_tokens(removed)

    async def retrieve(self, *args: Any, **kwargs: Any) -> None:
        """Retrieve not implemented."""
        raise NotImplementedError(
            f"retrieve not implemented in {self.__class__.__name__}"
        )
