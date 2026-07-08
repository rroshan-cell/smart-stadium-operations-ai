class Utils {
    /**
     * Centralized fetch wrapper with timeout and error handling.
     * @param {string} url - Target URL.
     * @param {RequestInit} options - Fetch options.
     * @param {number} timeoutMs - Timeout in milliseconds.
     */
    static async safeFetch(url, options = {}, timeoutMs = 8000) {
        const controller = new AbortController();
        const id = setTimeout(() => controller.abort(), timeoutMs);
        
        const mergedOptions = {
            ...options,
            signal: controller.signal,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, mergedOptions);
            clearTimeout(id);
            
            if (!response.ok) {
                let errDetail = `Status: ${response.status} ${response.statusText}`;
                try {
                    const json = await response.json();
                    if (json && json.error) errDetail = json.error;
                    else if (json && json.detail) errDetail = typeof json.detail === 'string' ? json.detail : JSON.stringify(json.detail);
                } catch (_) {}
                throw new Error(errDetail);
            }
            return await response.json();
        } catch (error) {
            clearTimeout(id);
            let message = error.message;
            if (error.name === 'AbortError') {
                message = 'Request timed out (server unreachable).';
            }
            console.error(`[API ERROR] Fetch failed for ${url}:`, error);
            throw new Error(message);
        }
    }

    /**
     * Formats numbers to string with thousand separators.
     * @param {number|string} val 
     */
    static formatNumber(val) {
        const num = Number(val);
        return isNaN(num) ? '0' : num.toLocaleString();
    }

    /**
     * Extracts HH:MM:SS or HH:MM from an ISO date string or Date object.
     * @param {string|Date} dateVal 
     */
    static formatTime(dateVal) {
        const date = typeof dateVal === 'string' ? new Date(dateVal) : dateVal;
        if (isNaN(date.getTime())) return '--:--:--';
        return date.toTimeString().split(' ')[0];
    }

    /**
     * Helper to parse simple markdown to HTML securely.
     * Supports: bold (**text**), bullet lists, and paragraphs.
     * @param {string} text 
     */
    static renderMarkdown(text) {
        if (!text) return '';
        // Escape HTML to prevent XSS
        let html = text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');

        // Replace bold **text** with <strong>
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Replace inline code `code` with <code>
        html = html.replace(/`(.*?)`/g, '<code>$1</code>');

        const lines = html.split('\n');
        let inUl = false;
        let inOl = false;
        const parts = [];

        lines.forEach(line => {
            const trimmed = line.trim();
            if (!trimmed) {
                // Blank line closes lists
                if (inUl) { parts.push('</ul>'); inUl = false; }
                if (inOl) { parts.push('</ol>'); inOl = false; }
                return;
            }

            const ulMatch = trimmed.match(/^[-*] (.+)/);
            const olMatch = trimmed.match(/^\d+\.\s+(.+)/);

            if (ulMatch) {
                if (!inUl) { if (inOl) { parts.push('</ol>'); inOl = false; } parts.push('<ul>'); inUl = true; }
                parts.push(`<li>${ulMatch[1]}</li>`);
            } else if (olMatch) {
                if (!inOl) { if (inUl) { parts.push('</ul>'); inUl = false; } parts.push('<ol>'); inOl = true; }
                parts.push(`<li>${olMatch[1]}</li>`);
            } else {
                if (inUl) { parts.push('</ul>'); inUl = false; }
                if (inOl) { parts.push('</ol>'); inOl = false; }
                parts.push(trimmed);
            }
        });

        if (inUl) parts.push('</ul>');
        if (inOl) parts.push('</ol>');

        // Join non-list text lines with <br> instead of wrapping each in <p>
        // Group consecutive plain text segments together
        let result = '';
        let textBuffer = [];
        parts.forEach(part => {
            if (part.startsWith('<ul>') || part.startsWith('</ul>') ||
                part.startsWith('<ol>') || part.startsWith('</ol>') ||
                part.startsWith('<li>')) {
                if (textBuffer.length) { result += textBuffer.join('<br>'); textBuffer = []; }
                result += part;
            } else {
                textBuffer.push(part);
            }
        });
        if (textBuffer.length) result += textBuffer.join('<br>');

        return result;
    }
}
window.Utils = Utils;
