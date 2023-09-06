import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
  ILabShell
} from '@jupyterlab/application';

import * as React from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import { codeList } from './code';
import { INotebookTools } from '@jupyterlab/notebook';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { JSONObject } from '@lumino/coreutils';

interface ICSSRule extends JSONObject {
    selector: string;
    styles: string[];
}

const extension: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-emil-enhanced:plugin',
  autoStart: true,
  requires: [INotebookTools, ILabShell, ISettingRegistry],
  activate: (
    app: JupyterFrontEnd,
    notebook: INotebookTools,
    shell: ILabShell, settingRegistry: ISettingRegistry
  ) => {
    console.log('JupyterLab extension jupyterlab-emil-enhanced is activated!');
    let styleElement = document.createElement("style");
    styleElement.type = "text/css";
    styleElement.id = "jupyterlab-emil-css";
    document.body.appendChild(styleElement);

    function updateOptions(settings: ISettingRegistry.ISettings): void {
            let styles = "";
            let rules = settings.composite.rules as ICSSRule[];
            for (let rule of rules) {
                styles += `${rule.selector} \{`;
                styles += "\n  " + rule.styles.join(";\n  ")
                styles += "\n}\n";
            }
            document.body.removeChild(styleElement);
            styleElement.innerHTML = styles;
            document.body.appendChild(styleElement);
        }
        settingRegistry
            .load(extension.id + ':plugin')
            .then(settings => {
                updateOptions(settings);
                settings.changed.connect(() => {
                    updateOptions(settings);
                });
            });




    let checkboxCopy = false;

    function SymbolsSidebar() {
      const list = codeList;
      return (
        <div className="sidebar-container">
          <div className="notice">
            Click on the icon will insert it to the cell
          </div>
          <label className="checkbox">
            <input
              type="checkbox"
              onChange={() => {
                checkboxCopy = !checkboxCopy;
              }}
            />
            Copy to clipboard
          </label>
          <div className="block-container">
            {list.map((item, i) => (
              <div
                className="block-container-element"
                key={i}
                onClick={() => iconClick(item.unicode)}
              >
                {item.unicode}
                <div>{item.name}</div>
              </div>
            ))}
          </div>
        </div>
      );
    }

    app.commands.addCommand('unicode:insert', {
      label: 'Insert Text',
      // isVisible: () => false,
      execute: args => {
        // input is JSON
        if (typeof args.text !== 'string') {
          return;
        } // if no text, return
        if (notebook.activeCell === null) {
          return;
        }
        notebook.activeCell.editor.replaceSelection &&
          notebook.activeCell.editor.replaceSelection(args.text.toString());
      }
    });

    function iconClick(code: any) {
      if (checkboxCopy) {
        navigator.clipboard.writeText(
          JSON.parse('["' + code + '"]')[0].toString()
        );
      } else {
        app.commands.execute('unicode:insert', {
          text: JSON.parse('["' + code + '"]')[0].toString()
        });
      }
    }

    const newWidget = () => {
      // Create a blank content widget inside of a MainAreaWidget
      const widget = ReactWidget.create(<SymbolsSidebar />);
      widget.id = 'jupyterlab-emil-enhanced';
      widget.title.label = 'Symbols';
      widget.title.closable = true;
      return widget;
    };
    const widget = newWidget();

    // let summary = document.createElement('p');
    // widget.node.appendChild(summary);
    // summary.innerText = "Hello, World!";

    shell.add(widget, 'left');
  }
};

export default extension;
