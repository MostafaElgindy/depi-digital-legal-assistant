/**
 * TOON (Token-Oriented Object Notation) Parser and Serializer for JavaScript
 * Compatible with Python TOON implementation
 */

class TOONParser {
    constructor() {
        this.pos = 0;
        this.text = '';
    }

    parse(text) {
        this.text = text.trim();
        this.pos = 0;
        this.skipWhitespaceAndComments();
        return this.parseValue();
    }

    skipWhitespaceAndComments() {
        while (this.pos < this.text.length) {
            // Skip whitespace
            if (/\s/.test(this.text[this.pos])) {
                this.pos++;
                continue;
            }

            // Skip comments (# to end of line)
            if (this.text[this.pos] === '#') {
                while (this.pos < this.text.length && this.text[this.pos] !== '\n') {
                    this.pos++;
                }
                continue;
            }

            break;
        }
    }

    parseValue() {
        this.skipWhitespaceAndComments();

        if (this.pos >= this.text.length) {
            return null;
        }

        const char = this.text[this.pos];

        // Object
        if (char === '{') {
            return this.parseObject();
        }

        // Array
        if (char === '[') {
            return this.parseArray();
        }

        // String
        if (char === '"' || char === "'") {
            return this.parseString();
        }

        // Unquoted value
        return this.parseUnquoted();
    }

    parseObject() {
        const obj = {};
        this.pos++; // skip '{'

        while (true) {
            this.skipWhitespaceAndComments();

            if (this.pos >= this.text.length || this.text[this.pos] === '}') {
                this.pos++;
                break;
            }

            // Parse key
            const key = this.parseKey();

            this.skipWhitespaceAndComments();

            // Expect colon
            if (this.pos >= this.text.length || (this.text[this.pos] !== ':' && this.text[this.pos] !== '=')) {
                throw new Error(`Expected ':' or '=' at position ${this.pos}`);
            }
            this.pos++;

            // Parse value
            const value = this.parseValue();
            obj[key] = value;

            this.skipWhitespaceAndComments();

            // Check for comma or end
            if (this.pos < this.text.length && this.text[this.pos] === ',') {
                this.pos++;
            } else if (this.pos < this.text.length && this.text[this.pos] !== '}') {
                throw new Error(`Expected ',' or '}' at position ${this.pos}`);
            }
        }

        return obj;
    }

    parseArray() {
        const arr = [];
        this.pos++; // skip '['

        while (true) {
            this.skipWhitespaceAndComments();

            if (this.pos >= this.text.length || this.text[this.pos] === ']') {
                this.pos++;
                break;
            }

            const value = this.parseValue();
            arr.push(value);

            this.skipWhitespaceAndComments();

            if (this.pos < this.text.length && this.text[this.pos] === ',') {
                this.pos++;
            } else if (this.pos < this.text.length && this.text[this.pos] !== ']') {
                throw new Error(`Expected ',' or ']' at position ${this.pos}`);
            }
        }

        return arr;
    }

    parseString() {
        const quote = this.text[this.pos];
        this.pos++;
        const start = this.pos;

        while (this.pos < this.text.length) {
            if (this.text[this.pos] === '\\' && this.pos + 1 < this.text.length) {
                this.pos += 2;
                continue;
            }

            if (this.text[this.pos] === quote) {
                const result = this.text.substring(start, this.pos);
                this.pos++;
                return this.unescapeString(result);
            }

            this.pos++;
        }

        throw new Error(`Unclosed string starting at position ${start}`);
    }

    parseKey() {
        this.skipWhitespaceAndComments();

        if (this.text[this.pos] === '"' || this.text[this.pos] === "'") {
            return this.parseString();
        } else {
            return this.parseIdentifier();
        }
    }

    parseIdentifier() {
        const start = this.pos;

        while (this.pos < this.text.length) {
            const char = this.text[this.pos];
            if (/[a-zA-Z0-9_\-.]/.test(char)) {
                this.pos++;
            } else {
                break;
            }
        }

        return this.text.substring(start, this.pos);
    }

    parseUnquoted() {
        const start = this.pos;

        while (this.pos < this.text.length) {
            const char = this.text[this.pos];
            if (/[a-zA-Z0-9_\-+.eE]/.test(char)) {
                this.pos++;
            } else {
                break;
            }
        }

        const value = this.text.substring(start, this.pos);

        // Check for boolean
        if (value.toLowerCase() === 'true') {
            return true;
        }
        if (value.toLowerCase() === 'false') {
            return false;
        }
        if (value.toLowerCase() === 'null' || value.toLowerCase() === 'nil') {
            return null;
        }

        // Try to parse as number
        if (!isNaN(value)) {
            return value.includes('.') ? parseFloat(value) : parseInt(value);
        }

        return value;
    }

    unescapeString(s) {
        const replacements = {
            '\\n': '\n',
            '\\t': '\t',
            '\\r': '\r',
            '\\\\': '\\',
            '\\"': '"',
            "\\'": "'"
        };

        for (const [old, replacement] of Object.entries(replacements)) {
            s = s.split(old).join(replacement);
        }

        return s;
    }
}

class TOONSerializer {
    constructor(pretty = true, indent = 2) {
        this.pretty = pretty;
        this.indent = indent;
        this.currentIndent = 0;
    }

    serialize(obj) {
        this.currentIndent = 0;
        return this.serializeValue(obj);
    }

    serializeValue(obj) {
        if (obj === null) {
            return 'null';
        }

        if (typeof obj === 'boolean') {
            return obj ? 'true' : 'false';
        }

        if (typeof obj === 'number') {
            return String(obj);
        }

        if (typeof obj === 'string') {
            return this.serializeString(obj);
        }

        if (Array.isArray(obj)) {
            return this.serializeArray(obj);
        }

        if (typeof obj === 'object') {
            return this.serializeObject(obj);
        }

        return this.serializeString(String(obj));
    }

    serializeObject(obj) {
        if (Object.keys(obj).length === 0) {
            return '{}';
        }

        const lines = ['{'];
        this.currentIndent += this.indent;

        const items = Object.entries(obj);
        items.forEach((item, i) => {
            const [key, value] = item;
            let line = ' '.repeat(this.currentIndent) + `${key}: ${this.serializeValue(value)}`;
            if (i < items.length - 1) {
                line += ',';
            }
            lines.push(line);
        });

        this.currentIndent -= this.indent;
        lines.push(' '.repeat(this.currentIndent) + '}');

        return this.pretty ? lines.join('\n') : lines.join('');
    }

    serializeArray(arr) {
        if (arr.length === 0) {
            return '[]';
        }

        const isSimple = arr.every(item => 
            typeof item !== 'object' || item === null
        );

        if (!this.pretty || isSimple) {
            const items = arr.map(item => this.serializeValue(item));
            return '[' + items.join(', ') + ']';
        }

        const lines = ['['];
        this.currentIndent += this.indent;

        arr.forEach((item, i) => {
            let line = ' '.repeat(this.currentIndent) + this.serializeValue(item);
            if (i < arr.length - 1) {
                line += ',';
            }
            lines.push(line);
        });

        this.currentIndent -= this.indent;
        lines.push(' '.repeat(this.currentIndent) + ']');

        return this.pretty ? lines.join('\n') : lines.join('');
    }

    serializeString(s) {
        if (this.needsQuotes(s)) {
            const escaped = s
                .replace(/\\/g, '\\\\')
                .replace(/"/g, '\\"')
                .replace(/\n/g, '\\n')
                .replace(/\t/g, '\\t');
            return `"${escaped}"`;
        }
        return s;
    }

    needsQuotes(s) {
        if (!s) return true;
        if (['true', 'false', 'null', 'nil'].includes(s.toLowerCase())) return true;
        if (/^[+\-]?\d/.test(s)) return true;
        if (!/^[a-zA-Z0-9_\-\.]+$/.test(s)) return true;
        return false;
    }
}

// Global functions
function parseTOON(text) {
    const parser = new TOONParser();
    return parser.parse(text);
}

function serializeTOON(obj, pretty = true) {
    const serializer = new TOONSerializer(pretty);
    return serializer.serialize(obj);
}

// Aliases
const toonLoads = parseTOON;
const toonDumps = serializeTOON;
