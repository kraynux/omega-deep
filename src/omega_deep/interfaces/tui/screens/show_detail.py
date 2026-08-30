# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran de detail d'une analyse : hosts + ports/services + graphe
d'architecture + export. Adapte de screens/show_detail.py d'omega-check
(D-007/D-008) — divergences DEEP : plusieurs hosts (HostsTable choisit
lequel peupler dans ServicesTable) et une section graphe en plus.

Le graphe est ici une liste texte des aretes (source -> cible, relation,
confiance) : suffisant pour un terminal, contrairement a l'export HTML ou
un vrai diagramme dessine est requis (D-009, voir
infrastructure/exporters/html_exporter.py) — un widget de dessin de graphe
dans le TUI n'a pas ete demande et ajouterait de la complexite non
justifiee ici (le texte reste lisible pour un graphe de cette taille)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, DataTable, Footer, Header, Static

from omega_deep.domain.architecture.models import ArchitectureGraph
from omega_deep.domain.scans.models import Scan
from omega_deep.domain.targets.models import Host
from omega_deep.interfaces.tui.screens._base import OmegaScreen
from omega_deep.interfaces.tui.screens.export_dialog import ExportDialogScreen
from omega_deep.interfaces.tui.widgets.hosts_table import HostsTable
from omega_deep.interfaces.tui.widgets.services_table import ServicesTable

if TYPE_CHECKING:
    from omega_deep.app.dependency_container import DependencyContainer


class ShowDetailScreen(OmegaScreen):
    def __init__(
        self,
        *,
        container: DependencyContainer,
        scan: Scan,
        hosts: tuple[Host, ...],
        graph: ArchitectureGraph | None,
    ) -> None:
        super().__init__()
        self._container = container
        self._scan = scan
        self._hosts = hosts
        self._hosts_by_ip = {host.ip: host for host in hosts}
        self._graph = graph

    def compose(self) -> ComposeResult:
        scan = self._scan
        yield Header()
        with VerticalScroll(classes="omega-panel"):
            yield Static(f"ANALYSE {scan.id}", classes="omega-title")
            yield Static(
                f"Cible racine : {scan.target} ({scan.target_ip}) — profil {scan.profile_name or '-'} — "
                f"statut {scan.status.value} — {len(scan.discovered_targets)} cible(s) decouverte(s)",
                classes="omega-subtitle",
            )

            yield Static("Hosts", classes="omega-subtitle")
            yield HostsTable(id="hosts-table")

            yield Static("Ports / services du host selectionne", classes="omega-subtitle")
            yield ServicesTable(id="services-table")

            yield Static("Graphe d'architecture", classes="omega-subtitle")
            with Vertical(id="graph-panel"):
                yield Static(self._graph_lines(), id="graph-lines")

            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Exporter", id="export", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(HostsTable).set_hosts(self._hosts)
        self.query_one(ServicesTable).set_host(self._hosts[0] if self._hosts else None)

    def _graph_lines(self) -> str:
        graph = self._graph
        if graph is None or not graph.edges:
            return "Aucune relation detectee."
        return "\n".join(
            f"{edge.source_ip} -[{edge.relation_type}, {edge.confidence.value}]-> {edge.target_ip}"
            for edge in graph.edges
        )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.data_table.id != "hosts-table":
            return  # ne reagit pas aux selections dans ServicesTable elle-meme
        host = self._hosts_by_ip.get(str(event.row_key.value))
        self.query_one(ServicesTable).set_host(host)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
            return
        if event.button.id == "export":
            self.app.push_screen(
                ExportDialogScreen(container=self._container, scan=self._scan, active_theme=self.app.theme)
            )
