import { CommonModule } from '@angular/common';
import { Component, DestroyRef, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ChatMessage, ChatService, DocumentInfo, Source } from './chat.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  private readonly service = inject(ChatService);
  private readonly destroyRef = inject(DestroyRef);

  readonly messages = signal<ChatMessage[]>([
    { role: 'assistant', content: 'Hi! I’m your AI RAG Assistant. Ask me something, or upload a document and I’ll answer using the retrieved content.' }
  ]);
  readonly sources = signal<Source[]>([]);
  readonly documents = signal<DocumentInfo[]>([]);
  readonly input = signal('');
  readonly loading = signal(false);
  readonly uploading = signal(false);
  readonly error = signal('');

  constructor() {
    this.loadDocuments();
  }

  send(): void {
    const message = this.input().trim();
    if (!message || this.loading()) return;

    const history = this.messages().slice(-8);
    this.messages.update(items => [...items, { role: 'user', content: message }]);
    this.input.set('');
    this.sources.set([]);
    this.error.set('');
    this.loading.set(true);

    this.service.chat(message, history).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: response => {
        this.messages.update(items => [...items, { role: 'assistant', content: response.answer }]);
        this.sources.set(response.sources);
        this.loading.set(false);
      },
      error: err => {
        this.error.set(err?.error?.detail ?? 'Could not reach the backend. Check that FastAPI is running.');
        this.loading.set(false);
      }
    });
  }

  onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.send();
    }
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    this.uploading.set(true);
    this.error.set('');
    this.service.upload(file).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => {
        this.uploading.set(false);
        this.loadDocuments();
      },
      error: err => {
        this.error.set(err?.error?.detail ?? 'Upload failed.');
        this.uploading.set(false);
      }
    });
    input.value = '';
  }

  deleteDocument(name: string): void {
    this.service.deleteDocument(name).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => this.loadDocuments(),
      error: err => this.error.set(err?.error?.detail ?? 'Delete failed.')
    });
  }

  clearChat(): void {
    this.messages.set([{ role: 'assistant', content: 'New conversation started. Ask me anything about your indexed documents.' }]);
    this.sources.set([]);
    this.error.set('');
  }

  private loadDocuments(): void {
    this.service.documents().pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: docs => this.documents.set(docs),
      error: () => this.documents.set([])
    });
  }
}
