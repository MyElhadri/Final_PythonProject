class DrawingApp {
    constructor() {
        this.canvas = document.getElementById('drawingCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.isDrawing = false;
        this.initializeEventListeners();
        this.initializeTools();
    }
    initializeEventListeners() {
        this.canvas.addEventListener('mousedown', (e) => this.startDrawing(e));
        this.canvas.addEventListener('mousemove', (e) => this.draw(e));
        this.canvas.addEventListener('mouseup', () => this.stopDrawing());
        this.canvas.addEventListener('mouseout', () => this.stopDrawing());
    }
    initializeTools() {
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.setTool(btn.dataset.tool);
                document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });
        const colorPicker = document.getElementById('colorPicker');
        colorPicker.addEventListener('change', (e) => this.setColor(e.target.value));
        const sizeSlider = document.getElementById('sizeSlider');
        const sizeValue = document.getElementById('sizeValue');
        sizeSlider.addEventListener('input', (e) => {
            const size = e.target.value;
            sizeValue.textContent = `${size}px`;
            this.setSize(size);
        });
        document.getElementById('undoBtn').addEventListener('click', () => this.undo());
        document.getElementById('clearBtn').addEventListener('click', () => this.clear());
        document.getElementById('saveBtn').addEventListener('click', () => this.save());
    }
    getMousePos(e) {
        const rect = this.canvas.getBoundingClientRect();
        return [e.clientX - rect.left, e.clientY - rect.top];
    }
    async startDrawing(e) {
        this.isDrawing = true;
        const pos = this.getMousePos(e);
        await this.sendDrawEvent('mousedown', pos);
    }
    async draw(e) {
        if (!this.isDrawing) return;
        const pos = this.getMousePos(e);
        await this.sendDrawEvent('mousemove', pos);
    }
    async stopDrawing() {
        if (this.isDrawing) {
            this.isDrawing = false;
            await this.sendDrawEvent('mouseup', [0, 0]);
        }
    }
    async sendDrawEvent(type, pos) {
        try {
            const response = await fetch('/api/draw', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type, pos })
            });
            const data = await response.json();
            this.updateCanvas(data.image);
        } catch (error) {
            console.error('Error:', error);
        }
    }
    updateCanvas(imageData) {
        const img = new Image();
        img.onload = () => {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
            this.ctx.drawImage(img, 0, 0);
        };
        img.src = `data:image/png;base64,${imageData}`;
    }
    async setTool(tool) {
        await fetch('/api/tool', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tool })
        });
    }
    async setColor(color) {
        await fetch('/api/color', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ color })
        });
    }
    async setSize(size) {
        await fetch('/api/size', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ size })
        });
    }
    async undo() {
        await this.sendDrawEvent('undo', [0, 0]);
    }
    async clear() {
        await this.sendDrawEvent('clear', [0, 0]);
    }
    async save() {
        try {
            const response = await fetch('/api/save', { method: 'POST' });
            const data = await response.json();
            if (data.success) {
                alert('Artwork saved successfully!');
                window.location.href = '/gallery';
            }
        } catch (error) {
            console.error('Error saving artwork:', error);
        }
    }
}
document.addEventListener('DOMContentLoaded', () => {
    new DrawingApp();
});
