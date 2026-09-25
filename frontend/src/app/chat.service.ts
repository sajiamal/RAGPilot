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

@Injectable({ providedIn: 'root' })
export class ChatService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  chat(message: string, history: ChatMessage[]): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.baseUrl}/chat`, { message, history });
  }

  documents(): Observable<DocumentInfo[]> {
    return this.http.get<DocumentInfo[]>(`${this.baseUrl}/documents`);
  }

  upload(file: File): Observable<DocumentInfo> {
    const body = new FormData();
    body.append('file', file);
    return this.http.post<DocumentInfo>(`${this.baseUrl}/documents/upload`, body);
  }

  deleteDocument(name: string): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.baseUrl}/documents/${encodeURIComponent(name)}`);
  }
}
