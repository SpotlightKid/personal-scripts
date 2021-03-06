#!/bin/bash
#
# Submit GPG key to a list of keyservers
#
# source: https://paste.xinu.at/axX1B9w/

# curl -sSL https://sks-keyservers.net/status/ | hq 'table.list tr > td:nth-of-type(2)' text | cut -d'[' -f1
keyservers=(
    keys.gnupg.net
    keyserver.ubuntu.com
    pgp.key-server.io
    pgp.mit.edu
    cheipublice.ro
    key.adeti.org
    keys.andreas-puls.de
    keys.i2p-projekt.de
    keys.jhcloos.com
    keys.mental.cash
    keys2.kfwebs.net
    keyserver-01.2ndquadrant.com
    keyserver-02.2ndquadrant.com
    keyserver-03.2ndquadrant.com
    keyserver.bazon.ru
    keyserver.insect.com
    keyserver.mattrude.com
    keyserver.swabian.net
    keyserver.taygeta.com
    keyserver1.computer42.org
    pgp.cyberbits.eu
    pgp.philihp.com
    pgp.pm
    pgp.skewed.de
    pgp.surf.nl
    pgp.uni-mainz.de
    pgpkeys.co.uk
    pgpkeys.eu
    pgpkeys.uk
    pgpkeys.urown.net
    sks.e-utp.net
    sks.hnet.se
    sks.infcs.de
    sks.pod01.fleetstreetops.com
    sks.pod02.fleetstreetops.com
    sks.srv.dumain.com
    a.keys.wolfined.com
    a.keyserver.alteholz.eu
    a.sks.srv.scientia.net
    ams.sks.heypete.com
    cheipublice.md
    conflux.pgp.intern.ccs-baumann.de
    disunitedstates.com
    fks.pgpkeys.eu
    gpg.phillymesh.net
    gpg.planetcyborg.de
    healthcheck-lb1.mj2.uk
    hockey.ecrypted.ml
    ice.mudshark.org
    key.bbs4.us
    key.blackbearinfosec.com
    key.cccmz.de
    key.ip6.li
    key1.dock23.de
    key2.dock23.de
    keys-01.licoho.de
    keys-02.licoho.de
    keys.bonus-communis.eu
    keys.communityrack.org
    keys.connectical.com
    keys.digitalis.org
    keys.exosphere.de
    keys.fedoraproject.org
    keys.fspproductions.biz
    keys.indymedia.org
    keys.internet-sicherheit.de
    keys.jpbe.de
    keys.nerds.lu
    keys.niif.hu
    keys.ppcis.net
    keys.riverwillow.net.au
    keys.s-l-c.biz
    keys.sbell.io
    keys.schluesselbruecke.de
    keys.sflc.info
    keys.stueve.us
    keys.techwolf12.nl
    keys.thoma.cc
    keys.void.gr
    keys2.flanga.io
    keyserv.sr32.net
    keyserver.adamas.ai
    keyserver.aktronic.de
    keyserver.arihanc.com
    keyserver.bau5net.com
    keyserver.blazrsoft.com
    keyserver.blupill.com
    keyserver.bonus-communis-bibliotheca.eu
    keyserver.boquet.org
    keyserver.borgnet.us
    keyserver.br.nucli.net
    keyserver.brian.minton.name
    keyserver.cdresel.de
    keyserver.cns.vt.edu
    keyserver.codinginfinity.com
    keyserver.compbiol.bio.tu-darmstadt.de
    keyserver.dacr.hu
    keyserver.dobrev.eu
    keyserver.durcheinandertal.ch
    keyserver.ecrypted.ml
    keyserver.eddiecornejo.com
    keyserver.gingerbear.net
    keyserver.globale-gruppe.de
    keyserver.iseclib.ru
    keyserver.ispfontela.es
    keyserver.kim-minh.com
    keyserver.kjsl.com
    keyserver.kjsl.org
    keyserver.kolosowscy.pl
    keyserver.layer42.net
    keyserver.leg.uct.ac.za
    keyserver.linuxpro.nl
    keyserver.lohn24-datenschutz.de
    keyserver.mesh.deuxpi.ca
    keyserver.mik-net.de
    keyserver.mobexpert.ro
    keyserver.mpi-bremen.de
    keyserver.nausch.org
    keyserver.oeg.com.au
    keyserver.opensuse.org
    keyserver.paulfurley.com
    keyserver.pch.net
    keyserver.provonet.nl
    keyserver.saol.no-ip.com
    keyserver.secretresearchfacility.com
    keyserver.securitytext.org
    keyserver.serviz.fr
    keyserver.siccegge.de
    keyserver.sincer.us
    keyserver.skoopsmedia.net
    keyserver.stack.nl
    keyserver.syseleven.de
    keyserver.timlukas.de
    keyserver.undergrid.net
    keyserver.ut.mephi.ru
    keyserver.vanbaak.eu
    keyserver.vi-di.fr
    keyserver.za.nucli.net
    keyserver.zap.org.au
    keyserver1.canonical.com
    keyserver2.canonical.com
    klucze.achjoj.info
    kr-sks.salac.me
    minsky.surfnet.nl
    node3.sks.mj2.uk
    node4.sks.mj2.uk
    openpgp-keyserver.eu
    openpgp1.claruscomms.net
    pgp.archreactor.org
    pgp.benny-baumann.de
    pgp.boomer41.net
    pgp.cert.am
    pgp.ext.selfnet.de
    pgp.gwolf.org
    pgp.jjim.de
    pgp.lehigh.edu
    pgp.librelabucm.org
    pgp.megagod.net
    pgp.net.nz
    pgp.ocf.berkeley.edu
    pgp.ohai.su
    pgp.rouing.me
    pgp.unix.lu
    pgp.uplinklabs.net
    pgp.ustc.edu.cn
    pgpkeys.ch
    pgpkeys.hu
    pgpkeyserver.posteo.de
    ranger.ky9k.org
    schluesselkasten.wertarbyte.de
    sks-cmh.semperen.com
    sks-lhr.semperen.com
    sks-nrt.semperen.com
    sks-peer.spodhuis.org
    sks-server.randala.com
    sks.alpha-labs.net
    sks.b4ckbone.de
    sks.bonus-communis.eu
    sks.capalino.de
    sks.cloud.icij.org
    sks.daylightpirates.org
    sks.ecks.ca
    sks.eq.by
    sks.es.net
    sks.fidocon.de
    sks.funkymonkey.org
    sks.heikorichter.name
    sks.icij.org
    sks.keyservers.net
    sks.kserver.eu
    sks.mbk-lab.ru
    sks.mirror.square-r00t.net
    sks.mj2.uk
    sks.mrball.net
    sks.neel.ch
    sks.nimblesec.com
    sks.okoyono.de
    sks.openpgp-keyserver.de
    sks.parafoil.net
    sks.pkqs.net
    sks.rainydayz.org
    sks.rarc.net
    sks.research.nxfifteen.me.uk
    sks.stsisp.ro
    sks.theblains.org
    sks.undergrid.net
    sks1.home-v.ind.in
    sks2.home-v.ind.in
    sks2.inx.net.za
    skspub.ward.ie
    sparkkeys.jhcloos.com
    vanunu.calyxinstitute.org
    vm-keyserver.spline.inf.fu-berlin.de
    whippet.andrewg.com
    zimmermann.mayfirst.org
)

for i in "${keyservers[@]}"; do
    gpg --keyserver "$i" --send-key "$1"
done
