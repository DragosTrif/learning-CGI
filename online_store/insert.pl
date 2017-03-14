#!/usr/bin/perl

use strict;
use warnings;
use DBI;
use Carp 'croak';


my $user = 'root';
my $pw = 1;
# connect to MySQL
my $dbh = DBI->connect("DBI:mysql:host=localhost;port=3306", $user, $pw);
$dbh->do("USE my_store");
my $file = 'products.txt';
my $sql_products = <<"MySQL";
INSERT INTO products (product_name, product_desc, product_price)
VALUES (?, ?, ?)
MySQL
my $sth = $dbh->prepare($sql_products);
# open file 

open (PRODUCTS, '<', $file) or die "Canot open '$file' $!:";
while (my $line = <PRODUCTS>) {
	chomp $line;
	my ($id, $product, $desc, $price) = split/:/, $line;
	$sth->execute($product, $desc, $price);
}
