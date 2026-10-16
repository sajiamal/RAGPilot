
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from './environment';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface Source {
  document: string;
  chunk_id: number;
  score: number;
  preview: string;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
}

export interface DocumentInfo {
  name: string;
  chunks: number;
}

export type ChatStreamEvent =
  | { type: 'sources'; sources: Source[] }
  | { type: 'chunk'; text: string }
  | { type: 'done' };

@Injectable({ providedIn: 'root' })
export class ChatService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  chat(
    message: string,
    history: ChatMessage[]
  ): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(
      `${this.baseUrl}/chat`,
      { message, history }
    );
  }

  streamChat(
    message: string,
    history: ChatMessage[]
  ): Observable<ChatStreamEvent> {
    return new Observable<ChatStreamEvent>((subscriber) => {
      const controller = new AbortController();

      const startStreaming = async (): Promise<void> => {
        try {
          const response = await fetch(
            `${this.baseUrl}/chat/stream`,
            {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream'
              },
              body: JSON.stringify({ message, history }),
              signal: controller.signal
            }
          );

          if (!response.ok) {
            throw new Error(
              `Streaming request failed: HTTP ${response.status}`
            );
          }

          if (!response.body) {
            throw new Error(
              'Streaming is not supported by this response.'
            );
          }

          const reader = response.body.getReader();
          const decoder = new TextDecoder();

          let buffer = '';

          const processEvent = (rawEvent: string): void => {
            const lines = rawEvent.split('\n');

            const eventType = lines
              .find((line) => line.startsWith('event:'))
              ?.slice(6)
              .trim();

            const data = lines
              .filter((line) => line.startsWith('data:'))
              .map((line) => line.slice(5).trimStart())
              .join('\n');

            if (!eventType) {
              return;
            }

            if (eventType === 'sources') {
              subscriber.next({
                type: 'sources',
                sources: JSON.parse(data) as Source[]
              });
            } else if (eventType === 'chunk') {
              const parsed = JSON.parse(data) as { text: string };

              subscriber.next({
                type: 'chunk',
                text: parsed.text
              });
            } else if (eventType === 'done') {
              subscriber.next({ type: 'done' });
            } else if (eventType === 'error') {
              const parsed = JSON.parse(data) as {
                message: string;
              };

              throw new Error(parsed.message);
            }
          };

          while (true) {
            const { done, value } = await reader.read();

            if (done) {
              break;
            }

            buffer += decoder.decode(value, { stream: true });

            buffer = buffer.replace(/\r\n/g, '\n');

            const events = buffer.split('\n\n');

            buffer = events.pop() ?? '';

            for (const event of events) {
              processEvent(event);
            }
          }

          buffer += decoder.decode();

          if (buffer.trim()) {
            processEvent(buffer);
          }

          subscriber.complete();
        } catch (error) {
          if (!subscriber.closed) {
            subscriber.error(error);
          }
        }
      };

      void startStreaming();

      return () => {
        controller.abort();
      };
    });
  }

  documents(): Observable<DocumentInfo[]> {
    return this.http.get<DocumentInfo[]>(
      `${this.baseUrl}/documents`
    );
  }

  upload(file: File): Observable<DocumentInfo> {
    const body = new FormData();

    body.append('file', file);

    return this.http.post<DocumentInfo>(
      `${this.baseUrl}/documents/upload`,
      body
    );
  }

  deleteDocument(
    name: string
  ): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(
      `${this.baseUrl}/documents/${encodeURIComponent(name)}`
    );
  }
}
