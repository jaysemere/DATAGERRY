/*
* DATAGERRY - OpenSource Enterprise CMDB
* Copyright (C) 2019 - 2021 NETHINKS GmbH
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
* along with this program. If not, see <https://www.gnu.org/licenses/>.
*/

import {
  Component,
  EventEmitter,
  HostListener,
  Input,
  OnChanges,
  OnInit,
  Output,
  SimpleChanges
} from '@angular/core';
import { ToastService } from '../../../layout/toast/toast.service';
import { SearchResultList } from '../../models/search-result';

export interface ReSearchParameters {
  rebuild: boolean;
  query: any[];
}

@Component({
  selector: 'cmdb-search-result-bar',
  templateUrl: './search-result-bar.component.html',
  styleUrls: ['./search-result-bar.component.scss']
})

export class SearchResultBarComponent implements OnInit, OnChanges {

  @Output() refreshSearch = new EventEmitter<ReSearchParameters>();
  @Input() queryParameters: any;
  @Input() searchResultList: SearchResultList;
  @Input() referenceResultList: SearchResultList;
  @Input() filterResultList: any[];

  // Filterers results
  public preSelectedFilterList: any[] = [];
  private rollbackQueryParameters: string = '';

  constructor(private toast: ToastService) {
  }

  public ngOnInit(): void {
    this.rollbackQueryParameters = this.queryParameters;
    this.addPreSelectedFilterItem(this.queryParameters);

  }

  public ngOnChanges(changes: SimpleChanges): void {
    this.preSelectedFilterList = [];
    this.addPreSelectedFilterItem(this.queryParameters);
  }

  @HostListener('window:scroll')
  onWindowScroll() {
    const dialog = document.getElementsByClassName('object-view-navbar') as HTMLCollectionOf<any>;
    dialog[0].id = 'result-bar-action';
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
      dialog[0].style.visibility = 'visible';
      dialog[0].classList.add('shadow');
    } else {
      dialog[0].classList.remove('shadow');
      dialog[0].id = '';
    }
  }

  private addPreSelectedFilterItem(value: string): void {
    JSON.parse(value).filter(f => {
      if (f.hasOwnProperty('settings')) {
        this.preSelectedFilterList = [...this.preSelectedFilterList,
          {
            total: 0,
            searchText: f.searchLabel,
            searchForm: 'type',
            searchLabel: f.searchLabel,
            settings: f.settings.types
          }
        ];
      }
    });
  }

  public rollbackQueryParametersIfNeeded(): void {
    this.reSearch(JSON.parse(this.rollbackQueryParameters), true);
  }

  private reSearch(value: any[], refreshFilter: boolean = false) {
    if (this.preSelectedFilterList.length === 0) {
      this.refreshSearch.emit({ rebuild: true, query: JSON.parse(this.rollbackQueryParameters) });
      this.addPreSelectedFilterItem(this.rollbackQueryParameters);
    } else {
      this.refreshSearch.emit({ rebuild: refreshFilter, query: value });
    }
  }

  public async delFilterItem(value: any) {
    const results = await this.filter(JSON.parse(this.queryParameters), value, async f => {
      await Promise.resolve();
      return f;
    });
    this.reSearch(results);
  }

  public async addFilterItem(value: any) {
    let queryJson = await this.filter(JSON.parse(this.queryParameters), value, async f => {
      await Promise.resolve();
      return f;
    });

    queryJson = queryJson.concat(
      {
        searchText: value.searchLabel,
        searchForm: 'type',
        searchLabel: value.searchLabel,
        settings: value.settings
      });
    queryJson = queryJson.filter(f => !f.hasOwnProperty('disjunction')).concat({
      searchText: 'or', searchForm: 'disjunction', searchLabel: 'or', disjunction: true
    });
    this.reSearch(queryJson);
  }

  async filter(arr: any[], value, callback) {
    const fail = Symbol();
    return (await Promise.all(arr.map(async item => (await callback(item)) ? item : fail))).filter(f =>
      f.searchLabel !== value.searchLabel);
  }

  public copyToClipboard() {
    const parsedUrl = new URL(window.location.href);
    const baseUrl = parsedUrl.origin;
    const selBox = document.createElement('textarea');
    selBox.value = `${ baseUrl }/search?query=${ this.queryParameters }`;
    this.generateDataForClipboard(selBox);
  }

  protected generateDataForClipboard(selBox: any) {
    selBox.style.position = 'fixed';
    selBox.style.left = '0';
    selBox.style.top = '0';
    selBox.style.opacity = '0';
    document.body.appendChild(selBox);
    selBox.focus();
    selBox.select();
    this.showToast(selBox);
  }

  protected showToast(selBox: any) {
    document.execCommand('copy');
    document.body.removeChild(selBox);
    this.toast.info('Content was copied to clipboard');
  }
}
