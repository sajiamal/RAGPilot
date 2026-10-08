
import { Pipe, PipeTransform } from '@angular/core';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

@Pipe({
  name: 'markdown',
  standalone: true,
  pure: true
})
export class MarkdownPipe implements PipeTransform {
  transform(content: string): string {
    const html = marked.parse(content, {
      async: false,
      gfm: true,
      breaks: true
    });

    return DOMPurify.sanitize(html);
  }
}
