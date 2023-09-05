import{I as o,r as e,b as t,d as n,i,m as s,n as c,s as a,x as l,S as r,K as d,a0 as h}from"./index-38064e7a.js";import"./c.171b378c.js";import{c as u,C as p,b as g}from"./c.ff7c761e.js";import{s as w}from"./c.a6e96e5a.js";class m{constructor(){this.chunks=""}transform(o,e){this.chunks+=o;const t=this.chunks.split("\r\n");this.chunks=t.pop(),t.forEach((o=>e.enqueue(o+"\r\n")))}flush(o){o.enqueue(this.chunks)}}class f extends HTMLElement{constructor(){super(...arguments),this.allowInput=!0}logs(){var o;return(null===(o=this._console)||void 0===o?void 0:o.logs())||""}connectedCallback(){if(this._console)return;if(this.attachShadow({mode:"open"}).innerHTML=`\n      <style>\n        :host, input {\n          background-color: #1c1c1c;\n          color: #ddd;\n          font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier,\n            monospace;\n          line-height: 1.45;\n          display: flex;\n          flex-direction: column;\n        }\n        form {\n          display: flex;\n          align-items: center;\n          padding: 0 8px 0 16px;\n        }\n        input {\n          flex: 1;\n          padding: 4px;\n          margin: 0 8px;\n          border: 0;\n          outline: none;\n        }\n        ${u}\n      </style>\n      <div class="log"></div>\n      ${this.allowInput?"<form>\n                >\n                <input autofocus>\n              </form>\n            ":""}\n    `,this._console=new p(this.shadowRoot.querySelector("div")),this.allowInput){const o=this.shadowRoot.querySelector("input");this.addEventListener("click",(()=>{var e;""===(null===(e=getSelection())||void 0===e?void 0:e.toString())&&o.focus()})),o.addEventListener("keydown",(o=>{"Enter"===o.key&&(o.preventDefault(),o.stopPropagation(),this._sendCommand())}))}const o=new AbortController,e=this._connect(o.signal);this._cancelConnection=()=>(o.abort(),e)}async _connect(o){this.logger.debug("Starting console read loop");try{await this.port.readable.pipeThrough(new TextDecoderStream,{signal:o}).pipeThrough(new TransformStream(new m)).pipeTo(new WritableStream({write:o=>{this._console.addLine(o.replace("\r",""))}})),o.aborted||(this._console.addLine(""),this._console.addLine(""),this._console.addLine("Terminal disconnected"))}catch(o){this._console.addLine(""),this._console.addLine(""),this._console.addLine(`Terminal disconnected: ${o}`)}finally{await w(100),this.logger.debug("Finished console read loop")}}async _sendCommand(){const o=this.shadowRoot.querySelector("input"),e=o.value,t=new TextEncoder,n=this.port.writable.getWriter();await n.write(t.encode(e+"\r\n")),this._console.addLine(`> ${e}\r\n`),o.value="",o.focus();try{n.releaseLock()}catch(o){console.error("Ignoring release lock error",o)}}async disconnect(){this._cancelConnection&&(await this._cancelConnection(),this._cancelConnection=void 0)}async reset(){this.logger.debug("Triggering reset."),await this.port.setSignals({dataTerminalReady:!1,requestToSend:!0}),await this.port.setSignals({dataTerminalReady:!1,requestToSend:!1}),await new Promise((o=>setTimeout(o,1e3)))}}customElements.define("ewt-console",f);let _=class extends a{constructor(){super(...arguments),this._isPico=!1}render(){return l`
      <mwc-dialog
        open
        .heading=${this.configuration?`Logs ${this.configuration}`:"Logs"}
        scrimClickAction
        @closed=${this._handleClose}
      >
        <ewt-console
          .port=${this.port}
          .logger=${console}
          .allowInput=${!1}
        ></ewt-console>
        <mwc-button
          slot="secondaryAction"
          label="Download Logs"
          @click=${this._downloadLogs}
        ></mwc-button>
        ${this.configuration?l`
              <mwc-button
                slot="secondaryAction"
                dialogAction="close"
                label="Edit"
                @click=${this._openEdit}
              ></mwc-button>
            `:""}
        ${this._isPico?"":l`
              <mwc-button
                slot="secondaryAction"
                label="Reset Device"
                @click=${this._resetDevice}
              ></mwc-button>
            `}
        <mwc-button
          slot="primaryAction"
          dialogAction="close"
          label="Close"
        ></mwc-button>
      </mwc-dialog>
    `}firstUpdated(o){super.firstUpdated(o),this.configuration&&r(this.configuration).then((o=>{this._isPico="RP2040"===o.esp_platform}))}async _openEdit(){this.configuration&&d(this.configuration)}async _handleClose(){await this._console.disconnect(),this.closePortOnClose&&await this.port.close(),this.parentNode.removeChild(this)}async _resetDevice(){await this._console.reset()}_downloadLogs(){h(this._console.logs(),(this.configuration?`${g(this.configuration)}_logs`:"logs")+".txt")}};_.styles=[o,e`
      mwc-dialog {
        --mdc-dialog-max-width: 90vw;
      }
      ewt-console {
        width: calc(80vw - 48px);
        height: calc(90vh - 128px);
      }
    `],t([n()],_.prototype,"configuration",void 0),t([n()],_.prototype,"port",void 0),t([n()],_.prototype,"closePortOnClose",void 0),t([i("ewt-console")],_.prototype,"_console",void 0),t([s()],_.prototype,"_isPico",void 0),_=t([c("esphome-logs-webserial-dialog")],_);
//# sourceMappingURL=c.3215b59d.js.map
