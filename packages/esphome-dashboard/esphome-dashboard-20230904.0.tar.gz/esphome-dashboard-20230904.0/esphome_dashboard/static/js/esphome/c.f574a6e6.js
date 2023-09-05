import{I as o,b as t,d as i,m as s,n as e,s as a,x as n,K as l,k as d}from"./index-38064e7a.js";import"./c.ff7c761e.js";import"./c.171b378c.js";let c=class extends a{render(){const o=void 0===this._valid?"":this._valid?"✅":"❌";return n`
      <esphome-process-dialog
        .heading=${`Validate ${this.configuration} ${o}`}
        .type=${"validate"}
        .spawnParams=${{configuration:this.configuration}}
        @closed=${this._handleClose}
        @process-done=${this._handleProcessDone}
      >
        <mwc-button
          slot="secondaryAction"
          dialogAction="close"
          label="Edit"
          @click=${this._openEdit}
        ></mwc-button>
        <mwc-button
          slot="secondaryAction"
          dialogAction="close"
          label="Install"
          @click=${this._openInstall}
        ></mwc-button>
      </esphome-process-dialog>
    `}_openEdit(){l(this.configuration)}_openInstall(){d(this.configuration)}_handleProcessDone(o){this._valid=0==o.detail}_handleClose(){this.parentNode.removeChild(this)}};c.styles=[o],t([i()],c.prototype,"configuration",void 0),t([s()],c.prototype,"_valid",void 0),c=t([e("esphome-validate-dialog")],c);
//# sourceMappingURL=c.f574a6e6.js.map
