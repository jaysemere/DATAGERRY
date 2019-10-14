/*
* DATAGERRY - OpenSource Enterprise CMDB
* Copyright (C) 2019 NETHINKS GmbH
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU Affero General Public License as
* published by the Free Software Foundation, either version 3 of the
* License, or (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU Affero General Public License for more details.

* You should have received a copy of the GNU Affero General Public License
* along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ImportService } from '../../import.service';

@Component({
  selector: 'cmdb-select-file',
  templateUrl: './select-file.component.html',
  styleUrls: ['./select-file.component.scss']
})
export class SelectFileComponent implements OnInit {

  private defaultFileFormat: string = '';
  public fileForm: FormGroup;
  public fileName: string = 'Choose file';
  public selectedFileFormat: string = `.${ this.defaultFileFormat }`;
  public importerTypes: any[] = [];

  @Output() public formatChange: EventEmitter<string>;
  @Output() public fileChange: EventEmitter<File>;

  public constructor(private importService: ImportService) {
    this.formatChange = new EventEmitter<string>();
    this.fileChange = new EventEmitter<File>();

    this.fileForm = new FormGroup({
      fileFormat: new FormControl(this.defaultFileFormat, Validators.required),
      file: new FormControl(null, Validators.required),
    });
  }

  public ngOnInit(): void {
    this.importService.getObjectImporters().subscribe(importers => {
      this.importerTypes = importers;
    });
    this.fileFormat.valueChanges.subscribe((format: string) => {
      this.formatChange.emit(format);
      this.selectedFileFormat = `.${ format }`;
    });
    this.file.valueChanges.subscribe((file) => {
      this.fileChange.emit(file);
    });
  }

  public get fileFormat() {
    return this.fileForm.get('fileFormat');
  }

  public get file() {
    return this.fileForm.get('file');
  }

  public selectFile(files) {
    if (files.length > 0) {
      const file = files[0];
      this.fileForm.get('file').setValue(file);
      this.fileName = file.name;
    }
  }

}