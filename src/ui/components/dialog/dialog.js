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
          <h2>Formulario</h2>
          
          <div class="form">
            <label>Nombre:</label>
            <input type="text" class="nombre" placeholder="Ingresa tu nombre">
            
            <label>Email:</label>
            <input type="email" class="email" placeholder="Ingresa tu email">
            
            <button>Guardar</button>
          </div>
        </div>
      </div>
    `;

    this.shadowRoot.getElementById('close-dialog-btn').addEventListener('click', () => {
      this.close();
    });

    this.shadowRoot.querySelector('.submit').addEventListener('click', () => {
      const nombre = this.shadowRoot.querySelector('.nombre').value;
      const email = this.shadowRoot.querySelector('.email').value;
      
      console.log('Nombre:', nombre);
      console.log('Email:', email);
      alert(`Datos: ${nombre} - ${email}`);
      
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