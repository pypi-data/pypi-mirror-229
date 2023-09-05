import{I as o,b as t,d as s,m as e,n as i,s as r,x as n,K as a}from"./index-38064e7a.js";import"./c.ff7c761e.js";import{o as l}from"./c.ac588108.js";import"./c.171b378c.js";import"./c.6975f5e9.js";import"./c.20adc540.js";let c=class extends r{render(){return n`
      <esphome-process-dialog
        always-show-close
        .heading=${`Logs ${this.configuration}`}
        .type=${"logs"}
        .spawnParams=${{configuration:this.configuration,port:this.target}}
        @closed=${this._handleClose}
        @process-done=${this._handleProcessDone}
      >
        <mwc-button
          slot="secondaryAction"
          dialogAction="close"
          label="Edit"
          @click=${this._openEdit}
        ></mwc-button>
        ${void 0===this._result||0===this._result?"":n`
              <mwc-button
                slot="secondaryAction"
                dialogAction="close"
                label="Retry"
                @click=${this._handleRetry}
              ></mwc-button>
            `}
      </esphome-process-dialog>
    `}_openEdit(){a(this.configuration)}_handleProcessDone(o){this._result=o.detail}_handleRetry(){l(this.configuration,this.target)}_handleClose(){this.parentNode.removeChild(this)}};c.styles=[o],t([s()],c.prototype,"configuration",void 0),t([s()],c.prototype,"target",void 0),t([e()],c.prototype,"_result",void 0),c=t([i("esphome-logs-dialog")],c);
//# sourceMappingURL=c.9da849b0.js.map
