class ModalDialog extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    this.shadowRoot.innerHTML = `
      <link rel="stylesheet" href="components/dialog/dialog.css">
      
      <div class="overlay">
        <div class="modal">
          <button id="close-dialog-btn" class="icon-btn close-dialog-btn close-btn">
            <svg width="28" height="28" viewBox="0 0 36 36">
                <path d="M28.5 9.62L26.38 7.5 18 15.88 9.62 7.5 7.5 9.62 15.88 18 7.5 26.38l2.12 2.12L18 20.12l8.38 8.38 2.12-2.12L20.12 18z"></path>
            </svg>
          </button>
          <h3 class="modal-title">Configuraciones</h3>
          <div class="modal-form">
            <div class="form-field">
              <label>Ntfy topic notifications</label>
              <input type="text" id="ntfyTopic" placeholder="Nombre del tema a subscribirse">   
            </div>         
            <button id="saveConfig">Guardar</button>
          </div>
        </div>
      </div>
    `;

    this.shadowRoot.getElementById('close-dialog-btn').addEventListener('click', () => {
      this.close();
    });

    this.shadowRoot.getElementById('saveConfig').addEventListener('click', () => {
      const ntfyTopic = this.shadowRoot.getElementById('ntfyTopic').value;
      console.log('ntfyTopic:', ntfyTopic);
      this.close();
    });

    this.shadowRoot.querySelector('.overlay').addEventListener('click', (e) => {
      if (e.target.className === 'overlay') {
        this.close();
      }
    });
  }

  open() {
    this.shadowRoot.querySelector('.overlay').style.display = 'flex';
  }

  close() {
    this.shadowRoot.querySelector('.overlay').style.display = 'none';
  }
}

customElements.define('modal-dialog', ModalDialog);